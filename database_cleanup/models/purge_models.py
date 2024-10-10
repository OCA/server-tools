# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

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


class CleanupPurgeLineModel(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.model"
    _description = "Cleanup Purge Line Model"

    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.model", "Purge Wizard", readonly=True
    )

    def purge(self):
        """
        Unlink models upon manual confirmation.
        """
        context_flags = {
            MODULE_UNINSTALL_FLAG: True,
            "purge": True,
        }

        if self:
            objs = self
        else:
            objs = self.env["cleanup.purge.line.model"].browse(
                self._context.get("active_ids")
            )
        for line in objs:
            self.env.cr.execute(
                "SELECT id, model from ir_model WHERE model = %s", (line.name,)
            )
            row = self.env.cr.fetchone()
            if not row:
                continue
            self.logger.info("Purging model %s", row[1])
            attachments = self.env["ir.attachment"].search(
                [("res_model", "=", line.name)]
            )
            if attachments:
                self.env.cr.execute(
                    "UPDATE ir_attachment SET res_model = NULL " "WHERE id in %s",
                    (tuple(attachments.ids),),
                )
            self.env["ir.model.constraint"].search(
                [
                    ("model", "=", line.name),
                ]
            ).unlink()
            relations = (
                self.env["ir.model.fields"]
                .search(
                    [
                        ("relation", "=", row[1]),
                    ]
                )
                .with_context(**context_flags)
            )
            for relation in relations:
                try:
                    # Fails if the model on the target side
                    # cannot be instantiated
                    relation.unlink()
                except KeyError:
                    _logger.error("")
                except AttributeError:
                    _logger.error("")
            self.env["ir.model.relation"].search(
                [("model", "=", line.name)]
            ).with_context(**context_flags).unlink()
            self.env["ir.model"].browse([row[0]]).with_context(**context_flags).unlink()
            line.write({"purged": True})
        return True


class CleanupPurgeWizardModel(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.model"
    _description = "Purge models"

    @api.model
    def find(self):
        """
        Search for models that cannot be instantiated.
        """
        res = []
        self.env.cr.execute("SELECT model from ir_model")
        for (model,) in self.env.cr.fetchall():
            if model not in self.env:
                res.append((0, 0, {"name": model}))
        if not res:
            raise UserError(_("No orphaned models found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.model", "wizard_id", "Models to purge"
    )
