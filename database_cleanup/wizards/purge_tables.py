# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models
from odoo.exceptions import UserError

_TABLE_TYPE_SELECTION = [
    ("base", "SQL Table"),
    ("view", "SQL View"),
]


class CleanupPurgeWizardTable(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.table"
    _description = "Purge tables"
    blacklist = [
        "endpoint_route",  # web-api/endpoint_route_handler
    ]

    @api.model
    def find(self):
        """
        Search for tables and views that cannot be instantiated.
        """
        known_tables = list(self.blacklist)
        models_in_registry = list(self.env.registry.models.keys())
        for model in self.env["ir.model"].search([("model", "in", models_in_registry)]):
            if model.model not in self.env:
                continue
            model_pool = self.env[model.model]
            known_tables.append(model_pool._table)
            known_tables += [
                column.relation
                for column in model_pool._fields.values()
                if column.type == "many2many"
                and (column.compute is None or column.store)
                and column.relation
            ]

        self.env.cr.execute(
            """
            SELECT table_name, table_type FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type in ('BASE TABLE', 'VIEW')
            AND table_name NOT IN %s""",
            (tuple(known_tables),),
        )

        res = [
            (
                0,
                0,
                {"name": row[0], "table_type": "view" if row[1] == "VIEW" else "base"},
            )
            for row in self.env.cr.fetchall()
        ]
        if not res:
            raise UserError(self.env._("No orphaned tables found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.table", "wizard_id", "Tables to purge"
    )
