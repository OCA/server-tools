# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval as eval
from odoo.exceptions import ValidationError


class RecordMergeCriteria(models.Model):
    _name = 'record.merge.criteria'
    _description = 'Record Merge by Criteria'
    _inherit = ['record.merge.mixin']

    domain = fields.Char(string="Filter", required=True)
    key = fields.Text(string="Group key", required=True,
                      help="The key that will be used to group the records to merge."
                           "It is based on the object with variable 'o', e.g. o.name.")
    group_ids = fields.One2many(
        comodel_name="record.merge.criteria.group",
        inverse_name="merge_id", string="Merge Groups")
    merge_ids = fields.One2many(
        comodel_name="record.merge.id",
        inverse_name="criteria_id",
        string="Merges")
    delete = fields.Selection(string="Default delete", selection=[
        ('delete', 'Delete'),
        ('deactivate', 'Deactivate'),
        ('recompute', 'Recompute'),
        ('sql', 'SQL delete'),
        ('none', 'None')], default="delete", required=True)

    model_name = fields.Char(string="Model name", related="model_id.model")

    merge_relation_id = fields.Many2one('record.merge.relation.field', string="Origin Relation")
    merge_id = fields.Many2one(
        'record.merge.id',
        string="Origin Merge",
        related="merge_relation_id.merge_id",
        store=True,
    )

    def get_records_to_merge(self):
        """
        get recordset of applied domain
        :return:
        """
        self.ensure_one()
        model_obj = self.env[self.model_id.model].sudo()
        domain = eval(self.domain)
        return model_obj.search(domain)

    def fill_group(self):
        """
        fills up the merge groups
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress'):
            model_id = merge.model_id
            model_obj = self.env[model_id.model]
            records = merge.get_records_to_merge()
            group_dict = {}
            for r in records:
                key = eval(merge.key,{'o': r})
                group_dict.setdefault(key, []).append(r.id)
            merge.group_ids.unlink()
            lines = []
            for ids in group_dict.values():
                if len(ids)>1:
                    destiny_record = model_obj.search(
                        [('id', 'in', ids)],
                        order=merge.order or model_obj._order,
                        limit=1
                    )
                    lines.append( (0, 0, {
                            'record_id': destiny_record.id,
                            'line_ids': [ (0, 0, {
                                'record_id': x
                            }) for x in ids]
                        })
                    )
            merge.group_ids = lines

    def create_merges(self):
        """
        creates merge by ids with the groups
        :return:
        """
        merge_id_obj = self.env['record.merge.id']
        for merge in self:
            if merge.merge_ids.filtered(lambda m: m.state not in ['draft', 'cancel']):
                raise ValidationError(
                    _('Cannot delete previous merges, please cancel them.')
                )
            merge.merge_ids.unlink()
            for group in merge.group_ids.filtered(lambda g: g.to_merge):
                lines = []
                for l in group.line_ids:
                    lines.append( (0, 0, {
                        'record_id': l.record_id,
                        'destiny': (l.record_id == group.record_id),
                    }))
                merge_id_obj.create({
                    'criteria_group_id': group.id,
                    'model_id': merge.model_id.id,
                    'name': _('Auto-merge for %s') % (','.join([str(x) for x in group.mapped('line_ids.record_id')])),
                    'id_line_ids': lines,
                    'order': merge.order,  # XXX: the order for selecting destiny is the order for consolidation?
                })

    # ACTION
    def action_merge_progress(self):
        self.write({'state': 'progress'})
        self.fill_group()
        self.fill_consolidate_field()
        self.fill_fk_field()
        self.fill_ref_field()
        self.fill_nonrel_field()
        self.fill_rec_field()

    def action_merge_cancel(self):
        self.write({'state': 'cancel'})

    def action_merge_all(self):
        """
        launch all processes of all children
        :return:
        """
        self.merge_ids.action_merge_all()

    def action_cancel_all(self):
        """
        cancel all children
        :return:
        """
        self.merge_ids.action_merge_cancel()

    def action_merge_done(self):
        self.write({'state': 'done'})
        self.create_merges()

    def action_refresh_group(self):
        self.fill_group()


class RecordMergeCriteriaGroup(models.Model):
    _name = 'record.merge.criteria.group'
    _description = 'Record Merge Group'
    _inherit = ['record.merge.mixin.id.line']

    merge_id = fields.Many2one('record.merge.criteria', string="Merge", required=True, ondelete='cascade')
    record_id = fields.Integer(string="Destiny ID")
    to_merge = fields.Boolean(string="Merge", default=True)
    to_delete = fields.Boolean(string="Delete after", default=True)
    line_ids = fields.One2many(
        comodel_name="record.merge.criteria.group.line",
        inverse_name="group_id", string="IDs to Merge")
    merge_ids = fields.One2many(
        comodel_name="record.merge.id",
        inverse_name="criteria_group_id", string="Merge by ID")


class RecordMergeCriteriaGroupLine(models.Model):
    _name = 'record.merge.criteria.group.line'
    _description = 'Record Merge Group Line'
    _rec_name = 'record_id'

    group_id = fields.Many2one('record.merge.criteria.group', string="Group", required=True, ondelete='cascade')
    record_id = fields.Integer(string="Merge ID", required=True)
