# -*- coding: utf-8 -*-
# © 2017 innoviù Srl <http://www.innoviu.com>
# © 2017 Agile Business Group Sagl <http://www.agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def domain_get(self, model_name, mode='read'):
        if 'bypass_record_rules' in self._context:
            # sudo() is not used here to prevent an infinite loop
            return [], [], ['"' + self.env[model_name]._table + '"']
        else:
            return super(IrRule, self).domain_get(model_name, mode=mode)
