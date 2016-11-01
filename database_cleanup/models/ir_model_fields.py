# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    # In case of purging it means the model does not exist anymore in
    # installed module. In this specific case, we need to avoid to check
    # if fields can be removed as it would fail.
    @api.multi
    def _prepare_update(self):
        if self.env.context.get('purge'):
            self -= self.filtered(lambda x: x.model not in self.env.registry)
        return super(IrModelFields, self)._prepare_update()
