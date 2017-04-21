# -*- coding: utf-8 -*-
# Copyright 2013 Agile Business Group sagl (http://www.agilebg.com)
# Copyright 2016 ACSONE SA/NA (http://acsone.eu)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = 'ir.model'

    avoid_quick_create = fields.Boolean()

    @api.multi
    def _patch_quick_create(self):

        def _wrap_name_create():
            def wrapper(self, *args, **kwargs):
                raise UserError(_("Can't create quickly. Opening create form"))
            return wrapper

        for model in self:
            if model.avoid_quick_create:
                model_name = model.model
                Model = self.pool.get(model_name)
                if Model and not hasattr(Model, 'check_quick_create'):
                    Model._patch_method('name_create', _wrap_name_create())
                    Model.check_quick_create = True
        return True

    def _register_hook(self):
        self.search([])._patch_quick_create()
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
