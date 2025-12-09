# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, models

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @api.model
    def _module_data_uninstall(self, modules_to_remove):
        """this function crashes for xmlids on undefined models or fields
        referring to undefined models"""
        for this in self.search([("module", "in", modules_to_remove)]):
            if this.model == "ir.model.fields":
                field = (
                    self.env[this.model]
                    .with_context(**{MODULE_UNINSTALL_FLAG: True})
                    .browse(this.res_id)
                )
                if not field.exists() or field.model not in self.env:
                    this.unlink()
                    continue
            if this.model not in self.env:
                this.unlink()
        return super()._module_data_uninstall(modules_to_remove)
