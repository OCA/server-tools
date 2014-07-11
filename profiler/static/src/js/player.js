openerp.profiler = function(instance) {
    instance.profiler.Player = instance.web.Widget.extend({
        template: 'profiler.player',
        events: {
            "click .profiler_enable": "enable",
            "click .profiler_disable": "disable",
            "click .profiler_clear": "clear",
            "click .profiler_dump": "dump",
        },
        apply_class: function(css_class) {
            console.log(css_class)
            this.$el.removeClass('profiler_player_enabled');
            this.$el.removeClass('profiler_player_disabled');
            this.$el.removeClass('profiler_player_clear');
            this.$el.addClass(css_class);
        },
        enable: function() {
            this.rpc('/web/profiler/enable', {});
            this.apply_class('profiler_player_enabled');
        },
        disable: function() {
            this.rpc('/web/profiler/disable', {});
            this.apply_class('profiler_player_disabled');
        },
        clear: function() {
            this.rpc('/web/profiler/clear', {});
            this.apply_class('profiler_player_clear');
        },
        dump: function() {
            $.blockUI();
            this.session.get_file({
                url: '/web/profiler/dump',
                complete: $.unblockUI
            });
        },
    });

    instance.web.UserMenu.include({
        do_update: function () {
            var self = this;
            this.update_promise.done(function () {
                self.rpc('/web/profiler/initial_state', {}).done(function(state) {
                    if (state.has_player_group) {
                        this.profiler_player = new instance.profiler.Player(this);
                        this.profiler_player.prependTo(instance.webclient.$('.oe_systray'));
                        this.profiler_player.apply_class(state.player_state);
                    }
                });
            });
            return this._super();
        },
    });
};
