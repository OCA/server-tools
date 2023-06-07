/*
    Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("module_analysis.web_client", function (require) {
    "use strict";

    const WebClient = require("web.WebClient");

    WebClient.include({
        /**
         * This is a docstring
         *
         * @returns {Boolean}
         */
        something_new: function () {
            console.log("something new");
            return true;
        },
    });

    return WebClient;
});
