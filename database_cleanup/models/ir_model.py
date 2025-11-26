# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
import logging

from odoo import api, models

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

_logger = logging.getLogger(__name__)


class IrModel(models.Model):
    _inherit = "ir.model"

    def _drop_table(self):
        """this function crashes for undefined models"""
        self = self.filtered(lambda x: x.model in self.env)
        return super()._drop_table()

    @api.depends()
    def _inherited_models(self):
        """this function crashes for undefined models"""
        self = self.filtered(lambda x: x.model in self.env)
        return super()._inherited_models()


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    def _prepare_update(self):
        """this function crashes for undefined models"""
        self = self.filtered(lambda x: x.model in self.env)
        return super()._prepare_update()


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
