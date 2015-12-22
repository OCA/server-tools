(function() {
    'use strict';
    $('.btn-reload').click(function(){
        $.ajax({
            url: "/instance_introspection/reload",
        }).done(function(html, el) {
            $('.repositories').html(html);
        });
    });
    $('.btn-reload').click();
})();
