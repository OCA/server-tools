odoo.define("mail.systray.PlayButtonMenu", function(require) {
    "use strict";

    var session = require("web.session");
    var SystrayMenu = require("web.SystrayMenu");
    var Widget = require("web.Widget");

    var PlayButtonMenu = Widget.extend({
        name: "play_button_menu",
        template: "mail.systray.PlayButtonMenu",
        events: {
            "click .o_record_security_group_button": "_onClickRecordSecurityGroup",
        },
        start: function() {
            return this._super.apply(this, arguments);
        },

        async willStart() {
            await this._super(...arguments);
            this.hasTechnicalSettingsGroup = await session.user_has_group(
                "base.group_system"
            );
        },

        _onClickRecordSecurityGroup: function() {
            this.$("#record_security_group_button").toggleClass("clicked");
            if (this.$("#record_security_group_button").hasClass("clicked")) {
                return this._rpc({
                    model: "res.users.profiler.sessions",
                    method: "create",
                    args: [
                        {
                            user_id: session.uid,
                            active: true,
                        },
                    ],
                });
            }
            var self = this;
            self._rpc({
                route: "/web/action/load",
                params: {
                    action_id:
                        "security_group_recorder.action_view_template_security_group_wizard",
                },
            }).then(function(action) {
                self.do_action(action, {
                    on_close: function() {
                        location.reload();
                    },
                });
            });
        },
    });

    SystrayMenu.Items.push(PlayButtonMenu);

    return PlayButtonMenu;
});
