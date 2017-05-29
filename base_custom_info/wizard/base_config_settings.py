# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = "base.config.settings"

    group_custom_info_manager = fields.Boolean(
        string="Manage custom information",
        implied_group="base_custom_info.group_basic",
        help="Allow all employees to manage custom information",
    )
    group_custom_info_partner = fields.Boolean(
        string="Edit custom information in partners",
        implied_group="base_custom_info.group_partner",
        help="Add a tab in the partners form to edit custom information",
    )
