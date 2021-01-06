# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def analyse_installed_modules(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        installed_modules = env["ir.module.module"].search(
            [("state", "=", "installed")]
        )
        installed_modules.button_analyse_code()
