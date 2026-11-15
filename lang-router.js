// Автоматическая подмена пути pages/ -> pages_<lang>/ при ?lang=xx
(function(){
    "use strict";
    try {
        var params = new URLSearchParams(window.location.search || "");
        var lang = params.get("lang");
        if (!lang || !/^(en|zh|hi|uk)$/.test(lang)) return;

        var prefix = "pages_" + lang + "/";

        // Сохраняем оригинальный open
        var origOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            try {
                if (typeof url === "string" && url.indexOf("pages/") === 0) {
                    url = prefix + url.substring("pages/".length);
                }
            } catch(e) {}
            return origOpen.apply(this, arguments);
        };
        console.log("[lang-router] enabled for", lang);
    } catch(e) {
        // Молча выходим — русская версия работает
    }
})();

// --- Мультиязычное меню (структура) ---
(function() {
    var params = new URLSearchParams(window.location.search);
    var lang = params.get('lang');
    if (!lang || lang === 'ru') return;

    fetch('structure_' + lang + '.json')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var flat = [];
            function walk(items) {
                for (var i = 0; i < items.length; i++) {
                    flat.push(items[i].title);
                    if (items[i].children && items[i].children.length > 0) {
                        walk(items[i].children);
                    }
                }
            }
            walk(data);

            var titles = document.querySelectorAll('.sidebar-menu .tree-title');
            for (var i = 0; i < titles.length && i < flat.length; i++) {
                if (flat[i]) {
                    titles[i].textContent = flat[i];
                }
            }
        })
        .catch(function(e) { console.warn('Menu translation failed:', e); });
})();
