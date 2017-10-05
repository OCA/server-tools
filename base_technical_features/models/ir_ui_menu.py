# coding: utf-8
# © 2016 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _visible_menu_ids(self, debug=False):
        """ Set debug = True, so that group_no_one is not filtered out of the
        user's groups """
        if not debug:
            debug = self.env.user.has_group(
                'base_technical_features.group_technical_features')
        return super(IrUiMenu, self)._visible_menu_ids(debug=debug)
