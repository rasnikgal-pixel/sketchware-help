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
