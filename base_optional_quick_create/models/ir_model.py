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

    def _patch_quick_create(self, cr, ids):

        def _wrap_name_create():
            def wrapper(self, cr, uid, name, context=None):
                raise orm.except_orm(
                    _('Error'),
                    _("Can't create quickly. Opening create form"))
            return wrapper

        for model in self.browse(cr, SUPERUSER_ID, ids):
            if model.avoid_quick_create:
                model_name = model.model
                model_obj = self.pool.get(model_name)
                if model_obj and not hasattr(model_obj, 'check_quick_create'):
                    model_obj._patch_method('name_create', _wrap_name_create())
                    model_obj.check_quick_create = True
        return True

    def _register_hook(self, cr):
        self._patch_quick_create(cr, self.search(cr, SUPERUSER_ID, []))
        return super(IrModel, self)._register_hook(cr)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        ir_model = super(IrModel, self).create(vals)
        self.pool[self._name]._patch_quick_create(self.env.cr, [ir_model.id])
        return ir_model

    @api.multi
    def write(self, vals):
        res = super(IrModel, self).write(vals)
        self.pool[self._name]._patch_quick_create(self.env.cr, self.ids)
        return res
