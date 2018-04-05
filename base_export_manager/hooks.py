# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from openerp import api, exceptions, SUPERUSER_ID
_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Loaded after installing the module.

    ``ir.exports.line.name`` was before a char field, and now it is a computed
    char field with stored values. We have to inverse it to avoid database
    inconsistencies.
    """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for export_line in env["ir.exports.line"].search([
            ("field1_id", "=", False),
            ("export_id", "!=", False),
            ("name", "!=", False),
        ]):
            try:
                export_line._inverse_name()
            except exceptions.ValidationError:
                export_line.active = False
                _logger.error(
                    'Deactivated invalid export line #%d', export_line,
                )
