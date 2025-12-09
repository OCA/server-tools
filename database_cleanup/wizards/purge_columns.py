# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models
from odoo.exceptions import UserError


class CleanupPurgeWizardColumn(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.column"
    _description = "Purge columns"

    # List of known columns in use without corresponding fields
    # Format: {table: [fields]}
    blacklist = {
        "wkf_instance": ["uid"],  # lp:1277899
        "res_users": ["password", "password_crypt", "totp_secret"],
        "res_partner": ["signup_token"],
    }

    @api.model
    def get_orphaned_columns(self, model_pools):
        """
        From openobject-server/openerp/osv/orm.py
        Iterate on the database columns to identify columns
        of fields which have been removed
        """
        columns = list(
            {
                column.name
                for model_pool in model_pools
                for column in model_pool._fields.values()
                if not (column.compute is not None and not column.store)
            }
        )
        columns += models.MAGIC_COLUMNS
        columns += self.blacklist.get(model_pools[0]._table, [])

        self.env.cr.execute(
            "SELECT a.attname FROM pg_class c, pg_attribute a "
            "WHERE c.relname=%s AND c.oid=a.attrelid AND a.attisdropped=False "
            "AND pg_catalog.format_type(a.atttypid, a.atttypmod) "
            "NOT IN ('cid', 'tid', 'oid', 'xid') "
            "AND a.attname NOT IN %s",
            (model_pools[0]._table, tuple(columns)),
        )
        return [column for (column,) in self.env.cr.fetchall()]

    @api.model
    def find(self):
        """
        Search for columns that are not in the corresponding model.

        Group models by table to prevent false positives for columns
        that are only in some of the models sharing the same table.
        Example of this is 'sale_id' not being a field of stock.picking.in
        """
        res = []

        # mapping of tables to tuples (model id, [pool1, pool2, ...])
        table2model = {}
        models_in_registry = list(self.env.registry.models.keys())
        for model in self.env["ir.model"].search([("model", "in", models_in_registry)]):
            if model.model not in self.env:
                continue
            model_pool = self.env[model.model]
            if not model_pool._auto:
                continue
            table2model.setdefault(model_pool._table, (model.id, []))[1].append(
                model_pool
            )

        for _table, model_spec in table2model.items():
            for column in self.get_orphaned_columns(model_spec[1]):
                res.append((0, 0, {"name": column, "model_id": model_spec[0]}))
        if not res:
            raise UserError(self.env._("No orphaned columns found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.column", "wizard_id", "Columns to purge"
    )
