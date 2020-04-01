# -*- coding: utf-8 -*-
# © 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import mute_logger


_logger = logging.getLogger('base.merge.wizard')


class BaseMergeWizard(models.TransientModel):

    _name = 'base.merge.wizard'

    model_id = fields.Many2one(
        'ir.model',
        # the client sets the current model in the context, we need this later
        default=lambda self: self.env['ir.model'].search([
            ('model', '=', self.env.context.get('active_model'))]),
        readonly=True,
        string="Model",
    )
    # We will make it look below as if this model has two fields:
    # target_id = fields.Many2one('the.model.mentioned.in.model_id')
    # source_ids = fields.Many2many('the.model.mentioned.in.model_id')
    # in order to hold the data for the above, we use base_sparse_field
    data = fields.Serialized()

    @api.model
    def default_get(self, fields_list):
        result = super(BaseMergeWizard, self).default_get(fields_list)
        if 'target_id' in fields_list:
            result['target_id'] = self.env.context.get('active_id')
        if 'source_ids' in fields_list:
            result['source_ids'] = [
                (6, 0, self.env.context.get('active_ids', [])),
            ]
        return result

    def fields_get(self, allfields=None, attributes=None):
        result = super(BaseMergeWizard, self).fields_get(
            allfields=allfields,
            attributes=attributes)
        # make copies here otherwise we edit the original
        # dictionary, and we don't want that.
        active_model = self.env.context.get('active_model') or 'ir.model'
        copy_dict = result.get('model_id') or {}
        result['target_id'] = copy_dict.copy()
        result['target_id']['relation'] = active_model
        result['target_id']['type'] = 'many2one'
        result['target_id']['string'] = 'Target record'
        result['target_id']['views'] = {}
        result['target_id']['readonly'] = False
        result['source_ids'] = copy_dict.copy()
        result['source_ids']['relation'] = active_model
        result['source_ids']['type'] = 'many2many'
        result['source_ids']['string'] = 'Source records'
        result['source_ids']['views'] = {}
        result['source_ids']['readonly'] = False
        return result

    @api.model
    def create(self, vals):
        # Upon clicking merge, this is where we enter first
        # Here we create a wizard object using only
        # data field, and remove what is not part
        # of our wizard model, while keeping ids
        vals['data'] = {
            'target_id': vals.pop('target_id', None),
            'source_ids': vals.pop('source_ids', [[None, None, []]])[0][2],
        }
        result = super(BaseMergeWizard, self).create(vals)
        # So what we do here and below, is to redirect writes
        # to our virtual fields into  data,
        # which we just make a dict of fieldnames->values. Y
        # vals[data] = {'target_id': vals.pop('target_id', None), etc}
        return result

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        needs_virtual = not fields or 'target_id' in fields or\
            'source_ids' in fields
        if fields and needs_virtual:
            fields = set(fields) - set(['target_id', 'source_ids'])
            fields.add('data')
        result = super(BaseMergeWizard, self).read(fields=fields, load=load)
        if needs_virtual:
            for record in result:
                record.update(dict(target_id=None, source_ids=None))
                record.update(record['data'] or {})
        return result

    def action_merge(self):
        self.ensure_one()
        model = self.env[self.model_id.model]
        target_record = model.browse(self.data['target_id'])
        source_records = model.browse(self.data['source_ids']) - target_record
        _logger.info(
            'I should merge all of %s into %s',
            source_records,
            target_record,
        )
        self._merge(source_records, target_record)
        return

    def action_merge_and_next_duplicate(self):
        """
        Duplicate records are merged in this methods,
        which is called by the user during interactive
        deduplication
        """
        return NotImplementedError(_('Currently not available'))

    def action_skip_and_next_duplicate(self):
        """ Skip a set of duplicates """
        return NotImplementedError(_('Currently not available'))

    def _merge(self, source_records, target_record):
        """ Merge source_records into target_record """
        if len(source_records) < 1:
            # Not enough records
            _logger.warning(
                'Not enough records provided for merging into %s',
                target_record,
            )
            return
        if len(source_records) > 5:
            # A lot of records
            _logger.warning(
                'Too many records provided for merging into %s',
                target_record,
            )
            return
            # Only admin should be able to do this
        if self.env.uid != SUPERUSER_ID:
            raise UserError(_("Only the Administrator can merge records"))
        # perform the actual merging
        self._update_foreign_keys(source_records, target_record)
        # and unlink records that are now merged
        source_records.unlink()

    @api.model
    def _update_foreign_keys(self, source_records, target_record):
        """
        This is where the actual merging takes place.
        We find constraints and relations (so many2one connections)
        of the records to be merged
        and update the target record to point to the relevant columns.
        """
        _logger.debug(
            '_update_foreign_keys for target: %s for source_records: %s',
            target_record.id,
            str(source_records.ids),
        )
        # Prepare to find fk columns for target/source model
        _table_name = target_record._table
        relations = self._get_foreign_keys(_table_name)
        for table, column in relations:
            query = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name LIKE '%s'
            """ % (table)
            self._cr.execute(query, ())
            columns = []
            for data in self._cr.fetchall():
                if data[0] != column:
                    columns.append(data[0])
            # do the update for the current table/column in SQL
            query_dic = {
                'table': table,  # this is the table that holds a relation
                'column': column,  # this is the related column to table
                'value': columns[0],  # this is the primary key (id)
            }
            with mute_logger('odoo.sql_db'), self._cr.savepoint():
                query = """
                    UPDATE "%(table)s"
                    SET "%(column)s" = %%s
                    WHERE "%(column)s"
                    IN %%s
                """ % query_dic
                self._cr.execute(
                    query,
                    (target_record.id, tuple(source_records.ids)),
                )

    def _get_foreign_keys(self, table):
        """
        Return a list of table/column pairs with relation to table argument.
        """
        query = """
            SELECT
                pg_class1.relname as table,
                pg_attribute1.attname as column
            FROM pg_constraint
                JOIN pg_class AS pg_class1 ON
                    pg_constraint.conrelid = pg_class1.oid
                JOIN pg_class AS pg_class2 ON
                    pg_constraint.confrelid = pg_class2.oid
                JOIN pg_attribute AS pg_attribute1 ON
                    pg_constraint.conkey[1] = pg_attribute1.attnum AND
                    pg_class1.oid = pg_attribute1.attrelid
                JOIN pg_attribute AS pg_attribute2 ON
                    pg_constraint.confkey[1] = pg_attribute2.attnum AND
                    pg_class2.oid = pg_attribute2.attrelid
            WHERE
                pg_class2.relname = %s AND
                pg_attribute2.attname = 'id' AND
                pg_constraint.contype = 'f'
        """
        self._cr.execute(query, (table,))
        return self._cr.fetchall()
