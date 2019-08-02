# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import psycopg2

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

_logger = logging.getLogger(__name__)

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'parent_left', 'parent_right',
                 '__last_update')


class RecordMergeId(models.Model):
    _name = 'record.merge.id'
    _description = 'Record Merge by Id'
    _inherit = ['record.merge.mixin']

    id_line_ids = fields.One2many(
        comodel_name="record.merge.id.line",
        inverse_name="merge_id",
        string="IDs to merge",
        copy=True,
    )
    relation_line_ids = fields.One2many(
        comodel_name="record.merge.relation.field",
        inverse_name="merge_id",
        string="Relation Fields")
    consolidate_order_ids = fields.One2many(
        comodel_name="record.merge.consolidate.order",
        inverse_name="merge_id", string="Fields to consolidate")

    destiny_id = fields.Integer(string="Destiny ID", compute="compute_destiny_id")
    delete_line_ids = fields.One2many(
        comodel_name="record.merge.id.delete",
        inverse_name="merge_id",
        string="IDs to delete")

    consolidate_done = fields.Boolean(string="Consolidate done", copy=False)
    fk_merge_done = fields.Boolean(string="FKs merge done", copy=False)
    ref_merge_done = fields.Boolean(string="References merge done", copy=False)
    nonrel_merge_done = fields.Boolean(string="Non-relational merge done", copy=False)
    recompute_fields_done = fields.Boolean(string="Recompute done", copy=False)
    delete_done = fields.Boolean(string="Delete done", copy=False)

    criteria_group_id = fields.Many2one(
        comodel_name="record.merge.criteria.group",
        string="Origin criteria group",
        copy=False,
    )
    criteria_id = fields.Many2one(
        comodel_name="record.merge.criteria",
        string="Origin criteria",
        related="criteria_group_id.merge_id",
        store=True,
    )
    merge_relation_id = fields.Many2one(
        'record.merge.relation.field',
        string="Origin Relation",
        copy=False,
    )
    merge_id = fields.Many2one(
        'record.merge.id',
        string="Origin Merge",
        related="merge_relation_id.merge_id",
        store=True,
    )

    # TODO: create log lines to avoid data loss
    # TODO: add active_test=False to all searches to find deactivated records?

    @api.multi
    @api.constrains('id_line_ids')
    def _check_quantity(self):
        for merge in self:
            destiny_count = len(merge.id_line_ids.filtered(lambda l: l.destiny))
            if destiny_count!=1:
                raise ValidationError(
                    _('There has to be one single destiny record for the merge.')
                )

    @api.depends('id_line_ids','id_line_ids.destiny')
    def compute_destiny_id(self):
        for merge in self:
            merge.destiny_id = merge.id_line_ids.filtered(lambda l: l.destiny).record_id

    def get_records_dict(self):
        """
        get a dict of records to merge
        :return:
        """
        self.ensure_one()
        res = {}
        model_obj = self.env[self.model_id.model].sudo()
        for line in self.id_line_ids:
            res.update({
                line.record_id: model_obj.browse(line.record_id)
            })
        return res

    def get_records_to_merge(self):
        """
        get recordset of all the ids minus the destiny
        :return:
        """
        self.ensure_one()
        model_obj = self.env[self.model_id.model].sudo()
        return model_obj.browse(self.id_line_ids.filtered(lambda l: not l.destiny).mapped('record_id'))

    def get_record_destiny(self):
        """
        get record of the destiny
        :return:
        """
        self.ensure_one()
        model_obj = self.env[self.model_id.model].sudo()
        return model_obj.browse(self.id_line_ids.filtered(lambda l: l.destiny).record_id)

    # RELATIONSHIPS
    def fill_relation(self):
        """
        fills up the relation lines
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress'):
            model_id = merge.model_id
            model_obj = self.env[model_id.model].sudo()
            all_records = model_obj.browse(merge.id_line_ids.mapped('record_id'))
            lines = []
            for f in model_id.field_id.filtered(lambda f:
                                                f.name not in MAGIC_COLUMNS and
                                                f.ttype in ['one2many', 'many2one']
                                                ):
                if getattr(all_records[0], f.name, False):  # bc DB errors or version changes can stop here
                    no_records = len(all_records.mapped(f.name))
                    if f.ttype=='one2many':
                        # we suggest it IF there are records in more than one of our records
                        count_records = len(all_records.filtered(
                            lambda r: r.mapped(f.name)
                        ))
                        if count_records>1:
                            lines.append(
                                (0, 0, {
                                    'field_id': f.id,
                                    'no_records': no_records,
                                })
                            )
                    elif f.ttype=='many2one':
                        # we suggest it IF there are more than one records in total
                        if no_records>1:
                            lines.append(
                                (0, 0, {
                                    'field_id': f.id,
                                    'no_records': no_records,
                                })
                            )
            merge.relation_line_ids.unlink()
            merge.relation_line_ids = lines

    # CONSOLIDATE
    def fill_consolidate_order(self):
        """
        fills up the consolidate order
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress'):
            record_ids = merge.id_line_ids.mapped('record_id')
            model_obj = self.env[merge.model_id.model].sudo()
            records = model_obj.search(
                [('id', 'in', record_ids)],
                order=merge.order or model_obj._order
            )
            lines = []
            for rec in records:
                lines.append(
                    (0, 0, {
                        'record_id': rec.id,
                    })
                )
            merge.consolidate_order_ids.unlink()
            merge.consolidate_order_ids = lines

    def consolidate(self):
        """
        consolidate fields in consolidate_field_ids
        with the order in consolidate_order_ids
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress' and not m.consolidate_done):
            if not merge.consolidate_field_ids or not merge.consolidate_order_ids:
                continue
            records = merge.get_records_dict()
            destiny_record = records.get(merge.destiny_id)
            vals = {}
            consolidated_order = merge.consolidate_order_ids.filtered(lambda r: r.to_merge).sorted(key=lambda r: r.sequence)
            for f in merge.consolidate_field_ids.filtered(lambda f: f.to_merge and f.field_id.name not in MAGIC_COLUMNS):
                consolidated_value = False
                for rec in consolidated_order:
                    # TODO: add explanation of order in ui
                    record = records.get(rec.record_id)
                    value = getattr(record, f.field_id.name, False)
                    # XXX: posibility of consolidating Falses
                    if value:
                        consolidated_value = value
                        break  # just get the first value
                if consolidated_value:
                    if f.field_id.ttype=='many2many':
                        vals[f.field_id.name] = [(6, 0, consolidated_value.ids)]
                    elif f.field_id.ttype=='many2one':
                        vals[f.field_id.name] = consolidated_value.id
                    else:
                        vals[f.field_id.name] = consolidated_value
            if vals:
                destiny_record.write(vals)
            # TODO: add message post
            merge.consolidate_done = True

    # FKS
    def fk_merge(self):
        """
        modify fk fields in fk_field_ids
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress' and not m.fk_merge_done):
            if not merge.fk_field_ids:
                continue
            destiny_record = merge.get_record_destiny()
            records_to_merge = merge.get_records_to_merge()

            for f in merge.fk_field_ids.filtered(lambda f: f.to_merge and f.field_id.name not in MAGIC_COLUMNS):
                table = f.table
                column = f.column
                # get list of columns of current table (exept the current fk column)
                query = "SELECT column_name FROM information_schema.columns WHERE table_name LIKE '%s'" % (table)
                self._cr.execute(query, ())
                columns = []
                for data in self._cr.fetchall():
                    if data[0] != column:
                        columns.append(data[0])

                # do the update for the current table/column in SQL
                query_dic = {
                    'table': table,
                    'column': column,
                    'value': columns[0],
                }
                if len(columns) <= 1:
                    # unique key treated
                    query = """
                        UPDATE "%(table)s" as ___tu
                        SET %(column)s = %%s
                        WHERE
                            %(column)s = %%s AND
                            NOT EXISTS (
                                SELECT 1
                                FROM "%(table)s" as ___tw
                                WHERE
                                    %(column)s = %%s AND
                                    ___tu.%(value)s = ___tw.%(value)s
                            )""" % query_dic
                    for rec in records_to_merge:
                        self._cr.execute(query, (destiny_record.id, rec.id, destiny_record.id))
                else:
                    try:
                        with mute_logger('odoo.sql_db'), self._cr.savepoint():
                            query = 'UPDATE "%(table)s" SET %(column)s = %%s WHERE %(column)s IN %%s' % query_dic
                            self._cr.execute(query, (destiny_record.id, tuple(records_to_merge.ids),))

                            # handle the recursivity with parent relation
                            if f.field_id.name==merge.model_id._parent_name and f.field_id.model==merge.model_id.model:
                                query = """
                                    WITH RECURSIVE cycle(id, %s) AS (
                                            SELECT id, %s FROM %s
                                        UNION
                                            SELECT  cycle.id, %s.%s
                                            FROM    %s, cycle
                                            WHERE   %s.id = cycle.%s AND
                                                    cycle.id != cycle.%s
                                    )
                                    SELECT id FROM cycle WHERE id = %s AND id = %%s
                                """ % (f.field_id.name,
                                       f.field_id.name,
                                       table,
                                       table,
                                       f.field_id.name,
                                       table,
                                       table,
                                       f.field_id.name,
                                       f.field_id.name,
                                       f.field_id.name,)
                                self._cr.execute(query, (destiny_record.id,))
                                # NOTE JEM : shouldn't we fetch the data ?
                    except psycopg2.Error as e:
                        # updating fails, most likely due to a violated unique constraint
                        # keeping record with nonexistent partner_id is useless, better delete it
                        query = 'DELETE FROM "%(table)s" WHERE "%(column)s" IN %%s' % query_dic
                        self._cr.execute(query, (tuple(records_to_merge.ids),))
            merge.fk_merge_done = True

    # REFERENCES e.g. field value = res.partner, 145
    def ref_merge(self):
        """
        modify fields in ref_field_ids
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress' and not m.ref_merge_done):
            if not merge.ref_field_ids:
                continue
            model_id = merge.model_id
            destiny_record = merge.get_record_destiny()
            records_to_merge = merge.get_records_to_merge()
            records_to_merge_ref = ['%s,%s' % (model_id.model, x.id) for x in records_to_merge]

            for f in merge.ref_field_ids.filtered(lambda f: f.to_merge and f.field_id.name not in MAGIC_COLUMNS):
                ref_field_id = f.field_id
                ref_model_obj = self.env[ref_field_id.model_id.model]
                ref_merge_records = ref_model_obj.search([
                    (ref_field_id.name, 'in', records_to_merge_ref),
                ])
                ref_merge_records.write({ref_field_id.name: '%s,%s' % (model_id.model, destiny_record.id)})
            merge.ref_merge_done = True

    # NON RELATIONAL e.g. two fields, one with model = res.partner, other res_id = 145
    def nonrel_merge(self):
        """
        modify fields in nonrel_field_ids
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress' and not m.nonrel_merge_done):
            if not merge.nonrel_field_ids:
                continue
            destiny_record = merge.get_record_destiny()
            records_to_merge = merge.get_records_to_merge()
            model_id = merge.model_id

            for f in merge.nonrel_field_ids.filtered(lambda f: f.to_merge and f.field_id.name not in MAGIC_COLUMNS):
                nonrel_id_field_id = f.field_id
                nonrel_model_field_id = f.model_field_id
                nonrel_model_obj = self.env[nonrel_model_field_id.model_id.model]
                nonrel_merge_records = nonrel_model_obj.search([
                    (nonrel_model_field_id.name, '=', model_id.model),
                    (nonrel_id_field_id.name, 'in', records_to_merge.ids),
                ])
                if nonrel_model_field_id.ttype=='char':
                    value = str(destiny_record.id)
                else:
                    value = destiny_record.id
                try:
                    nonrel_merge_records.write({nonrel_id_field_id.name: value})
                except psycopg2.IntegrityError as e:
                    # e.g. mail_followers that cannot be duplicated - postgres error
                    raise ValidationError(
                        _('There is an error when merging field %s from %s: %s. You could consider unchecking it.') % (
                            nonrel_id_field_id.name,
                            nonrel_id_field_id.model_id.name,
                            e.pgerror,
                        )
                    )
                except Exception as e:
                    raise ValidationError(
                        _('There is an error when merging field %s from %s: %s. You could consider unchecking it.') % (
                            nonrel_id_field_id.name,
                            nonrel_id_field_id.model_id.name,
                            e.message,
                        )
                    )
            merge.nonrel_merge_done = True

    # RECOMPUTE
    def recompute_fields(self):
        """
        modify fields in rec_field_ids
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress' and not m.recompute_fields_done):
            if not merge.rec_field_ids:
                continue
            destiny_record = merge.get_record_destiny()
            model_id = merge.model_id

            for f in merge.rec_field_ids.filtered(lambda f: f.to_merge and f.field_id.name not in MAGIC_COLUMNS):
                self.env.add_todo(destiny_record._fields[f.field_id.name], destiny_record)
            merge.recompute_fields_done = True

    # DELETE
    def fill_delete(self):
        """
        fills up the delete lines
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress' and not m.delete_done):
            lines = []
            for res_id in merge.id_line_ids.filtered(lambda l: not l.destiny).mapped('record_id'):
                lines.append(
                    (0, 0, {
                        'record_id': res_id,
                    })
                )
            merge.delete_line_ids.unlink()
            merge.delete_line_ids = lines

    def delete_records(self):
        """
        delete records in delete_line_ids
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress' and not m.delete_done):
            if not merge.delete_line_ids:
                continue
            model_id = merge.model_id
            model_obj = self.env[model_id.model]
            delete_ids = merge.delete_line_ids.filtered(lambda l: l.delete=='delete').mapped('record_id')
            if delete_ids:
                self.env[model_id.model].browse(delete_ids).unlink()
            deact_ids = merge.delete_line_ids.filtered(lambda l: l.delete=='deactivate').mapped('record_id')
            if deact_ids:
                self.env[model_id.model].browse(deact_ids).write({'active': False})
            recompute_ids = merge.delete_line_ids.filtered(lambda l: l.delete=='recompute').mapped('record_id')
            if recompute_ids:
                record_ids = model_obj.browse(recompute_ids)
                computed_fields = model_obj._field_computed
                stored_fields = [f.name for f in computed_fields if f.store]
                for sf in stored_fields:
                    field_id = model_id.field_id.filtered(lambda f: f.name == sf)
                    for rec in record_ids:
                        self.env.add_todo(rec._fields[field_id.name], rec)
            sql_ids = merge.delete_line_ids.filtered(lambda l: l.delete=='sql').mapped('record_id')
            if sql_ids:
                query = "DELETE FROM %s WHERE id in %%s" % (model_obj._table,)
                self.env.cr.execute(query, [tuple(sql_ids)])
            merge.delete_done = True

    # ACTION
    def action_merge_progress(self):
        self.write({'state': 'progress'})

        def clean_data(data_dict):
            keys_to_remove = ['create_uid', 'create_date', 'write_date', 'write_uid', '__last_update', 'id',
                              'merge_id', 'display_name', 'model_id']
            for k in keys_to_remove:
                data_dict.pop(k, None)
            return data_dict

        for merge in self:
            if not merge.criteria_id:
                merge.fill_relation()
                merge.fill_consolidate_field()
                merge.fill_consolidate_order()
                merge.fill_fk_field()
                merge.fill_ref_field()
                merge.fill_nonrel_field()
                merge.fill_rec_field()
                merge.fill_delete()
            else:
                merge.fill_relation()
                merge.fill_consolidate_order()
                merge.fill_delete()
                merge.mapped('delete_line_ids').write({'delete': merge.criteria_id.delete})
                values = {}
                for o2m_field_name in [
                    'consolidate_field_ids', 'fk_field_ids', 'ref_field_ids', 'nonrel_field_ids', 'rec_field_ids']:
                    line_values = []
                    for data_dict in getattr(merge.criteria_id, o2m_field_name).read(load=''):
                        line_values.append( (0, 0, clean_data(data_dict)) )
                    values[o2m_field_name] = line_values
                merge.write(values)

    def action_merge_cancel(self):
        self.write({'state': 'cancel'})

    def action_merge_all(self):
        """
        launch all processes
        :return:
        """
        self.filtered(lambda m: m.state=='draft').action_merge_progress()
        self.consolidate()
        self.fk_merge()
        self.ref_merge()
        self.nonrel_merge()
        self.recompute_fields()
        self.delete_records()
        self.write({'state': 'done'})

    def action_mark_done(self):
        """
        mark manually as done
        :return:
        """
        self.write({'state': 'done'})

    def action_refresh_consolidate(self):
        self.fill_consolidate_field()
        self.fill_consolidate_order()

    def action_refresh_fk_merge(self):
        self.fill_fk_field()

    def action_refresh_ref_merge(self):
        self.fill_ref_field()

    def action_refresh_nonrel_merge(self):
        self.fill_nonrel_field()

    def action_refresh_recompute(self):
        self.fill_rec_field()

    def action_refresh_delete(self):
        self.fill_delete()


class RecordMergeIdLine(models.Model):
    _name = 'record.merge.id.line'
    _description = 'Record Merge'
    _inherit = ['record.merge.mixin.id.line']

    merge_id = fields.Many2one('record.merge.id', string="Merge")
    destiny = fields.Boolean(string="Destiny")

    @api.onchange('destiny')
    def onchange_destiny(self):
        if self.destiny:
            self.merge_id.id_line_ids.filtered(
                lambda l: l.id != self.id
            ).write({'destiny': False})


class RecordMergeRelationField(models.Model):
    _name = 'record.merge.relation.field'
    _description = 'Relation Fields to consider'

    merge_id = fields.Many2one('record.merge.id', string="Merge", required=True)
    field_id = fields.Many2one('ir.model.fields', string="Field", required=True)
    no_records = fields.Integer(string="Number of records")
    ttype = fields.Selection(
        string='Field Type', selection=[
            ('one2many', 'one2many'),
            ('many2one', 'many2one')
        ],
        related='field_id.ttype'
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Relation Model',
        compute='_get_field_model',
        store=True,
    )

    merge_ids = fields.One2many(
        comodel_name="record.merge.id",
        inverse_name="merge_relation_id",
        string="Merges")
    criteria_ids = fields.One2many(
        comodel_name="record.merge.criteria",
        inverse_name="merge_relation_id",
        string="Criteria merges")

    @api.depends('field_id')
    def _get_field_model(self):
        model_obj = self.env['ir.model']
        for line in self:
            if line.field_id.relation:
                line.model_id = model_obj.search([
                    ('model', '=', line.field_id.relation)
                ], limit=1).id

    def create_relation_object(self):
        self.ensure_one()
        model_id = self.merge_id.model_id
        model_obj = self.env[model_id.model].sudo()
        all_records = model_obj.browse(self.merge_id.id_line_ids.mapped('record_id'))
        if self.ttype=='one2many':
            # create a criteria
            self.env['record.merge.criteria'].create({
                'name': _('Automatic criteria from %s') % (self.merge_id.model_id.model,),
                'model_id': self.env['ir.model'].search([('model', '=', self.field_id.relation)], limit=1).id,
                'domain': "[['project_id', 'in', %s]]" % (
                    tuple(self.merge_id.id_line_ids.mapped('record_id')),
                ),
                'key': 'TODO',
                'merge_relation_id': self.id,
            })
        elif self.ttype=='many2one':
            # create a merge by id
            rel_record_ids = all_records.mapped(self.field_id.name)
            lines = []
            for rec in rel_record_ids:
                lines.append((0, 0, {
                    'record_id': rec.id,
                    'destiny': (rec.id == rel_record_ids.ids[0]),
                }))

            self.env['record.merge.id'].create({
                'name': _('Automatic merge from %s') % (self.merge_id.model_id.model,),
                'model_id': self.env['ir.model'].search([('model', '=', self.field_id.relation)], limit=1).id,
                'id_line_ids': lines,
                'merge_relation_id': self.id,
            })

    def view_relation_object(self):
        self.ensure_one()
        if self.ttype=='one2many':
            # return a criteria
            if not self.criteria_ids:
                raise ValidationError(_('There are no criteria associated'))
            else:
                action = self.env['ir.actions.act_window'].for_xml_id('record_merge', 'record_merge_criteria_act_window')
                action.update({
                    'res_id': self.criteria_ids.id,
                    'views': [(False, 'form')],
                    'view_type': 'form',
                    'view_mode': 'form',
                })
                return action
        elif self.ttype=='many2one':
            # return a merge by id
            if not self.merge_ids:
                raise ValidationError(_('There are no merges associated'))
            else:
                action = self.env['ir.actions.act_window'].for_xml_id('record_merge', 'record_merge_id_act_window')
                action.update({
                    'res_id': self.merge_ids.id,
                    'views': [(False, 'form')],
                    'view_type': 'form',
                    'view_mode': 'form',
                })
                return action


class RecordMergeConsolidateOrder(models.Model):
    _name = 'record.merge.consolidate.order'
    _description = 'Fields to consolidate'
    _inherit = ['record.merge.mixin.id.line']
    _order = 'sequence asc'

    merge_id = fields.Many2one('record.merge.id', string="Merge")
    sequence = fields.Integer(string="Sequence", default=10)
    to_merge = fields.Boolean(string="Consolidate", default=True)


class RecordMergeIdDelete(models.Model):
    _name = 'record.merge.id.delete'
    _description = 'Delete Merged Record'
    _inherit = ['record.merge.mixin.id.line']

    merge_id = fields.Many2one('record.merge.id', string="Merge")
    delete = fields.Selection(string="To delete", selection=[
        ('delete', 'Delete'),
        ('deactivate', 'Deactivate'),
        ('recompute', 'Recompute'),
        ('sql', 'SQL delete'),
        ('none', 'None')], default="delete", required=True)

