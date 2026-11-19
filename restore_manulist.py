#!/usr/bin/env python3
import json, os, sys, shutil
from datetime import datetime, timezone

SRC        = os.path.expanduser("~/sketchware-help")
DST_ROOT   = os.path.expanduser("~/storage/shared/Project_ManuList")
PROJ_ID    = "sketchware-help"
PROJ_NAME  = "Sketchware Pro 7"
PROJ_DESC  = "Справка по Sketchware Pro 7"
PROJ_AUTHOR= "RasNikGal"

APPLY = "--apply" in sys.argv

def log(msg): print(msg)

def count_items(lst):
    n = 0
    for it in lst:
        n += 1
        if it.get("children"):
            n += count_items(it["children"])
    return n

def prune(lst, existing, removed):
    out = []
    for it in lst:
        has_file = it.get("file") and it["file"] in existing
        children = it.get("children") or []
        pruned_children = prune(children, existing, removed) if children else []
        if has_file:
            it["children"] = pruned_children
            out.append(it)
        else:
            if pruned_children:
                it2 = dict(it)
                it2.pop("file", None)
                it2["children"] = pruned_children
                out.append(it2)
            else:
                removed.append(it.get("title", "?") + " (" + str(it.get("file")) + ")")
    return out

def main():
    struct_path = os.path.join(SRC, "structure.json")
    if not os.path.isfile(struct_path):
        log("НЕТ structure.json"); return 1
    with open(struct_path, encoding="utf-8") as f:
        structure = json.load(f)
    pages_dir = os.path.join(SRC, "pages")
    existing = set(f for f in os.listdir(pages_dir) if f.endswith(".html"))
    removed = []
    clean = prune(structure, existing, removed)
    total_before = count_items(structure)
    total_after  = count_items(clean)
    live_pages   = sum(1 for f in existing)
    log("=== DRY-RUN ===" if not APPLY else "=== APPLY ===")
    log("SRC:        %s" % SRC)
    log("DST:        %s" % DST_ROOT)
    log("Разделов до:     %d" % total_before)
    log("Разделов после:  %d" % total_after)
    log("Страниц в pages/: %d" % live_pages)
    log("Удалено узлов:   %d" % len(removed))
    for r in removed:
        log("  - %s" % r)
    if not APPLY:
        log("\nЭто dry-run. Ничего не записано.")
        log("Для применения: python3 restore_manulist.py --apply")
        return 0
    proj_dir = os.path.join(DST_ROOT, "projects", PROJ_ID)
    pages_dst = os.path.join(proj_dir, "pages")
    img_dst   = os.path.join(proj_dir, "img")
    data_dir  = os.path.join(DST_ROOT, "data")
    os.makedirs(pages_dst, exist_ok=True)
    os.makedirs(img_dst,   exist_ok=True)
    os.makedirs(data_dir,  exist_ok=True)
    n_pages = 0
    for f in existing:
        shutil.copy2(os.path.join(pages_dir, f), os.path.join(pages_dst, f))
        n_pages += 1
    n_img = 0
    img_src = os.path.join(SRC, "img")
    if os.path.isdir(img_src):
        for f in os.listdir(img_src):
            s = os.path.join(img_src, f)
            if os.path.isfile(s):
                shutil.copy2(s, os.path.join(img_dst, f)); n_img += 1
    with open(os.path.join(proj_dir, "structure.json"), "w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)
    idx_src = os.path.join(SRC, "index.html")
    if os.path.isfile(idx_src):
        shutil.copy2(idx_src, os.path.join(proj_dir, "index.html"))
    project = {
        "id": PROJ_ID,
        "name": PROJ_NAME,
        "description": PROJ_DESC,
        "author": PROJ_AUTHOR,
        "sections_count": total_after,
        "created": datetime.now(timezone.utc).isoformat(),
        "default_template_index": 0
    }
    with open(os.path.join(proj_dir, "project.json"), "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)
    plist_path = os.path.join(data_dir, "projects.json")
    plist = []
    if os.path.isfile(plist_path):
        try:
            with open(plist_path, encoding="utf-8") as f:
                plist = json.load(f)
        except Exception:
            plist = []
    plist = [p for p in plist if p.get("id") != PROJ_ID]
    plist.append(project)
    with open(plist_path, "w", encoding="utf-8") as f:
        json.dump(plist, f, ensure_ascii=False, indent=2)
    log("\nГОТОВО:")
    log("  project dir: %s" % proj_dir)
    log("  pages:       %d" % n_pages)
    log("  img:         %d" % n_img)
    log("  projects.json: %s" % plist_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
