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
    $('#accordion').on('shown.bs.collapse', function () {
          var panel = $(this).find('.in');
          $('html, body').animate({
                      scrollTop: panel.offset().top
          }, 500);
    });
    $('#my-accordion').on('show hide', function() {
            $(this).css('height', 'auto');
    });
})();
