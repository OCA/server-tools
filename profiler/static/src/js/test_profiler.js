(function(){
    'use_strict';
    openerp.Tour.register({
        id: 'profile_run',
        name: 'Profile run',
        path: '/web',
        mode: 'test',
        steps: [
            {
                title: 'Check if is cleared',
                waitFor: 'li.oe_topbar_item.profiler_player.profiler_player_clear'
            },
            {
                title: 'Start profiling',
                onload: function () {
                    $('a.profiler_enable').trigger('click');
                }
            },
            {
                title: 'Check if is enabled',
                waitFor: 'li.oe_topbar_item.profiler_player.profiler_player_enabled'
            },
            {
                title: 'Stop profiling',
                onload: function () {
                    $('a.profiler_disable').trigger('click');
                }
            },
            {
                title: 'Check if is disabled',
                waitFor: 'li.oe_topbar_item.profiler_player.profiler_player_disabled'
            },
            {
                title: 'Dump profiling',
                onload: function () {
                    $('a.profiler_dump').trigger('click');
                }
            },
            {
                title: 'Clear profiling',
                onload: function () {
                    $('a.profiler_clear').trigger('click');
                }
            },
            {
                title: 'Check if is cleared again',
                waitFor: 'li.oe_topbar_item.profiler_player.profiler_player_clear'
            },

        ]
    });
}());
