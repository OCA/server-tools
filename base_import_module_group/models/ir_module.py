# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import AccessError


class IrModule(models.Model):

    _inherit = 'ir.module.module'

    @api.multi
    def _import_module(self, module, path, force=False):
        group_xid = 'base_import_module_group.group_module_import'
        if not self.env.user.has_group(group_xid):
            group = self.env.ref(group_xid)
            raise AccessError(
                _("Only users with group %s are allowed to import modules")
                % group.name
            )
        return super()._import_module(module, path, force=force)
