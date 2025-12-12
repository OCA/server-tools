# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import fields, models

from ..identifier_adapter import IdentifierAdapter


class CleanupPurgeLineColumn(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.column"
    _description = "Cleanup Purge Line Column"

    model_id = fields.Many2one("ir.model", "Model", required=True, ondelete="CASCADE")
    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.column", "Purge Wizard", readonly=True
    )

    def purge(self):
        """
        Unlink columns upon manual confirmation.
        """
        if self:
            objs = self
        else:
            objs = self.env["cleanup.purge.line.column"].browse(
                self._context.get("active_ids")
            )
        for line in objs:
            if line.purged:
                continue
            model_pool = self.env[line.model_id.model]
            # Check whether the column actually still exists.
            # Inheritance such as stock.picking.in from stock.picking
            # can lead to double attempts at removal
            self.env.cr.execute(
                "SELECT count(attname) FROM pg_attribute "
                "WHERE attrelid = "
                "( SELECT oid FROM pg_class WHERE relname = %s ) "
                "AND attname = %s",
                (model_pool._table, line.name),
            )
            if not self.env.cr.fetchone()[0]:
                continue

            self.logger.info(
                "Dropping column %s from table %s", line.name, model_pool._table
            )
            self.env.cr.execute(
                "ALTER TABLE %s DROP COLUMN %s",
                (IdentifierAdapter(model_pool._table), IdentifierAdapter(line.name)),
            )
            line.write({"purged": True})
            # we need this commit because the ORM will deadlock if
            # we still have a pending transaction
            self.env.cr.commit()  # pylint: disable=invalid-commit
        return True
