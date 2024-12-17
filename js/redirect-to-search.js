(function () {
    window.addEventListener('load', function () {
        var search_form = document.getElementById('docs-search');
        var search_input = document.getElementById('search-input');

        if (search_form) {
            search_form.addEventListener('submit', function (e) {
                e.preventDefault();
                window.location.href = search_input.getAttribute('search-url') + '?q=' + encodeURIComponent(search_input.value);
            });
        }
    });
})();
