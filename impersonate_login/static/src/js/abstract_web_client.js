// Copyright 2024 Akretion (https://www.akretion.com).
// @author Kévin Roche <kevin.roche@akretion.com>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
odoo.define("impersonate_login.AbstractWebClient", function (require) {
    "use strict";

    var AbstractWebClient = require("web.AbstractWebClient");
    var session = require("web.session");

    AbstractWebClient.include({
        _onWebClientStarted: function () {
            this._super.apply(this, arguments);
            if (session.impersonate_from_uid) {
                this.$el.addClass("o_is_impersonated");
            }
        },
    });
});
