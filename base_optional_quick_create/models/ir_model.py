# -*- coding: utf-8 -*-
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2016 ACSONE SA/NA (<http://acsone.eu>)

from openerp import api, fields, models
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


class IrModel(models.Model):
    _inherit = 'ir.model'

    avoid_quick_create = fields.Boolean()

    def _wrap_name_create(self, old_create, model):
        def wrapper(cr, uid, name, context=None):
            raise Warning(_("Can't create quickly. Opening create form"))
        return wrapper

    def _register_hook(self, cr, ids=None):
        if ids is None:
            ids = self.search(cr, SUPERUSER_ID, [])
        for model in self.browse(cr, SUPERUSER_ID, ids):
            if model.avoid_quick_create:
                model_name = model.model
                model_obj = self.pool.get(model_name)
                if model_obj and not hasattr(model_obj, 'check_quick_create'):
                    model_obj.name_create = self._wrap_name_create(
                        model_obj.name_create, model_name)
                    model_obj.check_quick_create = True

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        ir_model = super(IrModel, self).create(vals)
        self._register_hook(self.env.cr, [ir_model.id])
        return ir_model

    @api.multi
    def write(self, vals):
        res = super(IrModel, self).write(vals)
        self._register_hook(self.env.cr, [self.ids])
        return res
