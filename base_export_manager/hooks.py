# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """Loaded after installing the module.

    ``ir.exports.line.name`` was before a char field, and now it is a computed
    char field with stored values. We have to inverse it to avoid database
    inconsistencies.
    """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env["ir.exports.line"].search([
            ("field1_id", "=", False),
            ("export_id", "!=", False),
            ("name", "!=", False),
        ])._inverse_name()
