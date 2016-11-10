# -*- coding: utf-8 -*-
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2016 ACSONE SA/NA (<http://acsone.eu>)
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = 'ir.model'

    avoid_quick_create = fields.Boolean()

    @api.multi
    def _patch_quick_create(self):

        @api.multi
        def _wrap_name_create():
            def wrapper(self):
                raise UserError(_("Can't create quickly. Opening create form"))
            return wrapper

        for model in self:
            if model.avoid_quick_create:
                model_name = model.model
                model_obj = self.env.get(model_name)
                if (
                        not isinstance(model_obj, type(None)) and
                        not hasattr(model_obj, 'check_quick_create')):
                    model_obj._patch_method('name_create', _wrap_name_create())
                    model_obj.check_quick_create = True
        return True

    def _register_hook(self):
        models = self.search([])
        models._patch_quick_create()
        return super(IrModel, self)._register_hook()

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        ir_model = super(IrModel, self).create(vals)
        ir_model._patch_quick_create()
        return ir_model

    @api.multi
    def write(self, vals):
        res = super(IrModel, self).write(vals)
        self._patch_quick_create()
        return res
