// Copyright 2024 Akretion (https://www.akretion.com).
// @author Kévin Roche <kevin.roche@akretion.com>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

odoo.define("impersonate_login.UserMenu", function (require) {
    "use strict";

    var UserMenu = require("web.UserMenu");
    var core = require("web.core");
    var session = require("web.session");
    var _t = core._t;

    UserMenu.include({
        start: function () {
            this.toggleImpersonationLinks();
            return this._super.apply(this, arguments);
        },

        _onMenuImpersonate: function () {
            var self = this;
            this._rpc({
                model: "ir.model.data",
                method: "xmlid_to_res_model_res_id",
                args: ["impersonate_login.impersonate_res_users_tree"],
            }).then(function (data) {
                self.do_action({
                    type: "ir.actions.act_window",
                    name: _t("Users"),
                    res_model: "res.users",
                    target: "new",
                    view_mode: "list",
                    views: [[data[1], "list"]],
                    domain: [["share", "=", false]],
                });
            });
        },

        _onMenuOrigin_login: function () {
            var self = this;
            return self
                ._rpc({
                    model: "res.users",
                    method: "back_to_origin_login",
                    args: [],
                })
                .then(function () {
                    location.reload(true);
                });
        },

        toggleImpersonationLinks: function () {
            var returnToLogin = this.$('[data-menu="origin_login"]');
            var impersonateLogin = this.$('[data-menu="impersonate"]');
            if (session.impersonate_from_uid) {
                returnToLogin.removeClass("d-none");
                impersonateLogin.addClass("d-none");
            } else if (session.is_impersonate_user) {
                returnToLogin.addClass("d-none");
                impersonateLogin.removeClass("d-none");
            } else {
                returnToLogin.addClass("d-none");
                impersonateLogin.addClass("d-none");
            }
        },
    });
});
