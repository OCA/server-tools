# Copyright 2017 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import fields, models

from ..identifier_adapter import IdentifierAdapter


class CreateIndexesLine(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.create_indexes.line"
    _description = "Cleanup Create Indexes line"

    purged = fields.Boolean("Created")
    wizard_id = fields.Many2one("cleanup.create_indexes.wizard")
    field_id = fields.Many2one("ir.model.fields", required=True)

    def purge(self):
        for field in self.mapped("field_id"):
            model = self.env[field.model]
            name = f"{model._table}__{field.name}_index"
            self.env.cr.execute(
                "create index %s ON %s (%s)",
                (
                    IdentifierAdapter(name, quote=False),
                    IdentifierAdapter(model._table),
                    IdentifierAdapter(field.name),
                ),
            )
            self.env.cr.execute("analyze %s", (IdentifierAdapter(model._table),))
        self.write(
            {
                "purged": True,
            }
        )
