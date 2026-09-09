/*
    Copyright 2026 Akretion (http://www.akretion.com).
    @author Florian Mounier <florian.mounier@akretion.com>
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/
odoo.define("full_text_search.tsvector", function (require) {
    "use strict";

    const field_utils = require("web.field_utils");
    field_utils.parse.tsvector = (x) => x;
});
