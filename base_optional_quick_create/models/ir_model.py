# Copyright 2016 ACSONE SA/NV (https://acsone.eu)
# Copyright 2016 Akretion (Alexis de Lattre alexis.delattre@akretion.com)
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = 'ir.model'

    avoid_quick_create = fields.Boolean()

    @api.multi
    def _patch_quick_create(self):

        def _wrap_name_create():
            @api.model
            def wrapper(self, name):
                raise UserError(_(
                    "Can't create %s with name %s quickly.\n"
                    "Please contact your system administrator to disable "
                    "this behaviour.") % (self._name, name))
            return wrapper

        method_name = 'name_create'
        for model in self:
            model_obj = self.env.get(model.model)
            if model.avoid_quick_create:
                model_obj._patch_method(method_name, _wrap_name_create())
            else:
                method = getattr(model_obj, method_name, None)
                if method and hasattr(method, 'origin'):
                    model_obj._revert_method(method_name)
        return True

    def _register_hook(self):
        models = self.search([])
        models._patch_quick_create()
        return super()._register_hook()

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        ir_model = super().create(vals)
        ir_model._patch_quick_create()
        return ir_model

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        self._patch_quick_create()
        return res
