# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    # if previous configuration exist on delete_attachment_group_ids or
    # delete_attachment_user_ids, change the default level of
    # attachment deletion at 'custom' to keep it.
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        previous_group_or_user = False
        for model in env["ir.model"].search([]):
            if model.delete_attachment_group_ids or model.delete_attachment_user_ids:
                model.is_restrict_delete_attachment = True
                previous_group_or_user = True

        if previous_group_or_user:
            env["ir.config_parameter"].sudo().set_param(
                "restrict_delete_attachment", "custom"
            )
