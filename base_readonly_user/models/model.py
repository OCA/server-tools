# Copyright 2017 Lorenzo Battistini - Agile Business Group
# Copyright 2017 Alex Comba - Agile Business Group
# Copyright 2021 Lorenzo Battistini - TAKOBI
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from collections import defaultdict
from odoo import models, _, api
from odoo.exceptions import UserError
from odoo.modules.registry import Registry


class IrModel(models.Model):
    _inherit = 'ir.model'

    def _patch_readonly_user(self):

        def make_create():
            @api.model_create_multi
            def create(self, vals_list, **kw):
                if self.env.user.readonly_user:
                    raise UserError(
                        _("Readonly user can't create records"))
                else:
                    return create.origin(self, vals_list, **kw)
            return create

        def make_write():
            @api.multi
            def _write(self, vals, **kw):
                if self.env.user.readonly_user:
                    raise UserError(
                        _("Readonly user can't write records"))
                else:
                    return _write.origin(self, vals, **kw)
            return _write

        def make_unlink():
            @api.multi
            def unlink(self, **kwargs):
                if self.env.user.readonly_user:
                    raise UserError(
                        _("Readonly user can't delete records"))
                else:
                    return unlink.origin(self, **kwargs)
            return unlink

        patched_models = defaultdict(set)

        def patch(model, name, method):
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)

        for model in self.sudo().search([]):
            Model = self.env.get(model.model)
            if Model is not None:
                patch(Model, 'create', make_create())
                patch(Model, '_write', make_write())
                patch(Model, 'unlink', make_unlink())

    @api.model_cr
    def _register_hook(self):
        self._patch_readonly_user()

    def _unregister_hook(self):
        NAMES = ['create', '_write', 'unlink']
        for Model in self.env.registry.values():
            for name in NAMES:
                try:
                    delattr(Model, name)
                except AttributeError:
                    pass

    def _update_registry(self):
        if self.env.registry.ready:
            self._cr.commit()
            self.env.reset()
            registry = Registry.new(self._cr.dbname)
            registry.registry_invalidated = True

    @api.model
    def create(self, vals):
        res = super(IrModel, self).create(vals)
        self._update_registry()
        return res
