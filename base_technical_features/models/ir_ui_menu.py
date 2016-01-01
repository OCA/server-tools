# -*- coding: utf-8 -*-
from openerp import api, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _visible_menu_ids(self, debug=False):
        """ Set debug = True, so that group_no_one is not filtered out of the
        user's groups """
        if not debug:
            debug = self.pool['res.users'].has_group(
                self.env.cr, self.env.uid,
                'base_technical_features.group_technical_features')
        return super(IrUiMenu, self)._visible_menu_ids(debug=debug)
