# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..identifier_adapter import IdentifierAdapter


class CleanupPurgeLineColumn(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.column'

    model_id = fields.Many2one('ir.model', 'Model', required=True,
                               ondelete='CASCADE')
    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.column', 'Purge Wizard', readonly=True)

    @api.multi
    def purge(self):
        """
        Unlink columns upon manual confirmation.
        """
        if self:
            objs = self
        else:
            objs = self.env['cleanup.purge.line.column']\
                .browse(self._context.get('active_ids'))
        for line in objs:
            if line.purged:
                continue
            model_pool = self.env[line.model_id.model]
            # Check whether the column actually still exists.
            # Inheritance such as stock.picking.in from stock.picking
            # can lead to double attempts at removal
            self.env.cr.execute(
                'SELECT count(attname) FROM pg_attribute '
                'WHERE attrelid = '
                '( SELECT oid FROM pg_class WHERE relname = %s ) '
                'AND attname = %s',
                (model_pool._table, line.name))
            if not self.env.cr.fetchone()[0]:
                continue

            self.logger.info(
                'Dropping column %s from table %s',
                line.name, model_pool._table)
            self.env.cr.execute(
                'ALTER TABLE %s DROP COLUMN %s',
                (
                    IdentifierAdapter(model_pool._table),
                    IdentifierAdapter(line.name)
                ))
            line.write({'purged': True})
            # we need this commit because the ORM will deadlock if
            # we still have a pending transaction
            self.env.cr.commit()  # pylint: disable=invalid-commit
        return True


class CleanupPurgeWizardColumn(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.column'
    _description = 'Purge columns'

    # List of known columns in use without corresponding fields
    # Format: {table: [fields]}
    blacklist = {
        'wkf_instance': ['uid'],  # lp:1277899
    }

    @api.model
    def get_orphaned_columns(self, model_pools):
        """
        From openobject-server/openerp/osv/orm.py
        Iterate on the database columns to identify columns
        of fields which have been removed
        """
        columns = list(set([
            column.name
            for model_pool in model_pools
            for column in list(model_pool._fields.values())
            if not (column.compute is not None and not column.store)
        ]))
        columns += models.MAGIC_COLUMNS
        columns += self.blacklist.get(model_pools[0]._table, [])

        self.env.cr.execute(
            "SELECT a.attname FROM pg_class c, pg_attribute a "
            "WHERE c.relname=%s AND c.oid=a.attrelid AND a.attisdropped=False "
            "AND pg_catalog.format_type(a.atttypid, a.atttypmod) "
            "NOT IN ('cid', 'tid', 'oid', 'xid') "
            "AND a.attname NOT IN %s",
            (model_pools[0]._table, tuple(columns)))
        return [column for column, in self.env.cr.fetchall()]

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

        for model in self.env['ir.model'].search([]):
            if model.model not in self.env:
                continue
            model_pool = self.env[model.model]
            if not model_pool._auto:
                continue
            table2model.setdefault(
                model_pool._table, (model.id, [])
            )[1].append(model_pool)

        for table, model_spec in list(table2model.items()):
            for column in self.get_orphaned_columns(model_spec[1]):
                res.append((0, 0, {
                            'name': column,
                            'model_id': model_spec[0]}))
        if not res:
            raise UserError(_('No orphaned columns found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.column', 'wizard_id', 'Columns to purge')
