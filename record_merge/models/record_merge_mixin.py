# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class RecordMergeMixin(models.AbstractModel):
    _name = 'record.merge.mixin'

    name = fields.Char(required=True,
                       string='Name')
    model_id = fields.Many2one(
        comodel_name='ir.model',
        required=True, string='Model',
        ondelete='restrict')
    order = fields.Text(string="Order")
    state = fields.Selection(string="Selection", selection=[
        ('draft', 'Draft'),
        ('progress', 'In progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], default="draft", required=True)
    consolidate_field_ids = fields.One2many(
        comodel_name="record.merge.consolidate.field",
        inverse_name="merge_id", string="Fields to consolidate")
    fk_field_ids = fields.One2many(
        comodel_name="record.merge.fk.field",
        inverse_name="merge_id", string="FK fields to merge")
    ref_field_ids = fields.One2many(
        comodel_name="record.merge.ref.field",
        inverse_name="merge_id", string="Reference fields to merge")
    nonrel_field_ids = fields.One2many(
        comodel_name="record.merge.nonrel.field",
        inverse_name="merge_id", string="Non-relational fields to merge")
    rec_field_ids = fields.One2many(
        comodel_name="record.merge.rec.field",
        inverse_name="merge_id", string="Fields to recompute")

    def fill_consolidate_field(self):
        """
        fills up the consolidate field
        :return:
        """
        for merge in self.filtered(lambda m: m.state=='progress'):
            lines = []
            fields = merge.model_id.field_id.filtered(
                lambda f: f.ttype != 'one2many' and
                          not f.related and
                          not f.compute and
                          not f.readonly and
                          f.name not in MAGIC_COLUMNS)
            for f in fields:
                # we do not merge o2m and m2m by default
                # bc they will be done by fks
                to_merge = True
                if f.ttype in ('one2many', 'many2many'):
                    to_merge = False
                lines.append(
                    (0, 0, {
                        'field_id': f,
                        'to_merge': to_merge,
                    })
                )
            merge.consolidate_field_ids.unlink()
            merge.consolidate_field_ids = lines

    def fill_fk_field(self):
        """
        fills up the fk lines
        :return:
        """
        ir_model_obj = self.env['ir.model']
        ir_field_obj = self.env['ir.model.fields']
        for merge in self.filtered(lambda m: m.state=='progress'):
            model_obj = self.env[merge.model_id.model]
            table = model_obj._table
            query = """
                SELECT cl1.relname as table, att1.attname as column
                FROM pg_constraint as con, pg_class as cl1, pg_class as cl2, pg_attribute as att1, pg_attribute as att2
                WHERE con.conrelid = cl1.oid
                    AND con.confrelid = cl2.oid
                    AND array_lower(con.conkey, 1) = 1
                    AND con.conkey[1] = att1.attnum
                    AND att1.attrelid = cl1.oid
                    AND cl2.relname = %s
                    AND att2.attname = 'id'
                    AND array_lower(con.confkey, 1) = 1
                    AND con.confkey[1] = att2.attnum
                    AND att2.attrelid = cl2.oid
                    AND con.contype = 'f'
            """
            self._cr.execute(query, (table,))
            fks = self._cr.fetchall()

            lines = []
            for fk_table, fk_column in fks:
                # TODO: try except
                model_id = ir_model_obj.search([
                    ('model', '=ilike', fk_table),  # _ is the any single character pattern, so finds dots
                ])
                field_ids = []
                if model_id:
                    field_id = ir_field_obj.search([
                        ('model_id', '=', model_id.id),
                        ('name', '=', fk_column),
                    ])
                else:  # could be a m2m (wo class)
                    field_id = ir_field_obj.search([
                        ('relation_table', '=', fk_table),
                        ('column2', '=', fk_column),
                        ('id', 'not in', field_ids),  # case mail_message_res_partner_needaction_rel - two fields in the same m2m
                    ], limit=1)
                    if not field_id:  # could be a m2m defined in model_obj (e.g. brand_ids defined in rp)
                        field_id = ir_field_obj.search([
                            ('relation_table', '=', fk_table),
                            ('column1', '=', fk_column),
                            ('id', 'not in', field_ids),
                        ], limit=1)

                field_ids.append(field_id.id)
                lines.append(
                    (0, 0, {
                        'field_id': field_id.id,
                        'table': fk_table,
                        'column': fk_column,
                    })
                )
            merge.fk_field_ids.unlink()
            merge.fk_field_ids = lines

    @api.model
    def additional_ref_field(self):
        """
        inheritable method to get all other fields that follow the
         reference pattern but are not reference type
        :return: list of tuples: model name (dot notation), field name
        """
        # we do NOT want to merge ir.property with res_id, bc it has been merged in consolidattion
        return [
            ('ir.property', 'value_reference'),
        ]

    def fill_ref_field(self):
        """
        fills up the ref lines
        :return:
        """
        ir_model_obj = self.env['ir.model']
        ir_field_obj = self.env['ir.model.fields']
        for merge in self.filtered(lambda m: m.state=='progress'):
            lines = []
            model_id = merge.model_id
            records_to_merge = merge.get_records_to_merge()
            records_to_merge_ref = ['%s,%s' % (model_id.model, x.id) for x in records_to_merge]
            ref_field_ids = ir_field_obj.search([
                ('ttype', '=', 'reference'),
            ])  # field that is reference to the model
            # XXX: filter readonly?
            add_fields = self.additional_ref_field()
            for af in add_fields:
                af_model = ir_model_obj.search([
                    ('model', '=', af[0]),
                ])
                if af_model:
                    af_field = ir_field_obj.search([
                        ('model_id', '=', af_model.id),
                        ('name', '=', af[1]),
                    ])
                    if af_field:
                        ref_field_ids |= af_field

            for ref_field_id in ref_field_ids:
                ref_model_obj = self.env[ref_field_id.model_id.model]
                ref_merge_records = ref_model_obj.search([
                    (ref_field_id.name, 'in', records_to_merge_ref),
                ])  # this are the records that we could merge
                if ref_merge_records:
                    lines.append(
                        (0, 0, {
                            'field_id': ref_field_id.id,
                        })
                    )

            merge.ref_field_ids.unlink()
            merge.ref_field_ids = lines

    def fill_nonrel_field(self):
        """
        fills up the nonrel lines
        :return:
        """
        ir_model_obj = self.env['ir.model']
        ir_field_obj = self.env['ir.model.fields']
        for merge in self.filtered(lambda m: m.state=='progress'):
            lines = []
            records_to_merge = merge.get_records_to_merge()
            model_id = merge.model_id
            nonrel_model_field_ids = ir_field_obj.search([
                ('ttype', '=', 'many2one'),
                ('relation', '=', 'ir.model'),
                ('model', 'not like', 'record.merge%')
            ])  # field that is reference to the model
            # XXX: filter readonly?
            for nonrel_model_field_id in nonrel_model_field_ids:
                # only reference field if there is a res_id
                nonrel_id_field_id = nonrel_model_field_id.model_id.field_id.filtered(lambda f: f.name == 'res_id')
                if nonrel_id_field_id:
                    nonrel_model_obj = self.env[nonrel_model_field_id.model_id.model]
                    nonrel_merge_records = nonrel_model_obj.search([
                        (nonrel_model_field_id.name, '=', model_id.id),
                        (nonrel_id_field_id.name, 'in', records_to_merge.ids),
                    ])  # this are the records that we could merge
                    if nonrel_merge_records:
                        lines.append(
                            (0, 0, {
                                'field_id': nonrel_id_field_id.id,
                                'model_field_id': nonrel_model_field_id.id,
                            })
                        )

            nonrel_model_field_ids = ir_field_obj.search([
                ('ttype', '=', 'char'),
                ('name', 'in', ['model', 'res_model']),
            ])  # field that is reference to the model
            for nonrel_model_field_id in nonrel_model_field_ids:
                # only reference field if there is a res_id
                nonrel_id_field_id = nonrel_model_field_id.model_id.field_id.filtered(lambda f: f.name == 'res_id')
                if nonrel_id_field_id:
                    nonrel_model_obj = self.env[nonrel_model_field_id.model_id.model]
                    nonrel_merge_records = nonrel_model_obj.search([
                        (nonrel_model_field_id.name, '=', model_id.model),
                        (nonrel_id_field_id.name, 'in', records_to_merge.ids),
                    ])  # this are the records that we could merge
                    if nonrel_merge_records:
                        lines.append(
                            (0, 0, {
                                'field_id': nonrel_id_field_id.id,
                                'model_field_id': nonrel_model_field_id.id,
                            })
                        )

            merge.nonrel_field_ids.unlink()
            merge.nonrel_field_ids = lines

    def fill_rec_field(self):
        """
        fills up the rec lines
        :return:
        """
        ir_model_obj = self.env['ir.model']
        ir_field_obj = self.env['ir.model.fields']
        for merge in self.filtered(lambda m: m.state=='progress'):
            lines = []
            model_id = merge.model_id
            computed_fields = self.env[model_id.model]._field_computed
            stored_fields = [f.name for f in computed_fields if f.store]
            for sf in stored_fields:
                field_id = model_id.field_id.filtered(lambda f: f.name == sf)
                if field_id:
                    lines.append(
                        (0, 0, {
                            'field_id': field_id.id,
                        })
                    )
            merge.rec_field_ids.unlink()
            merge.rec_field_ids = lines


class RecordMergeMixinIdLine(models.AbstractModel):
    _name = 'record.merge.mixin.id.line'

    merge_id = fields.Many2one('record.merge.mixin', string="Merge")
    record_id = fields.Integer(string="ID", required=True)
    record_name = fields.Char(string="Name", compute="_compute_record_name", store=True)

    @api.multi
    @api.depends('record_id')
    def _compute_record_name(self):
        for rec in self.filtered(lambda r: r.record_id):
            model_obj = self.env[rec.merge_id.model_id.model]
            rec_instance = model_obj.browse(rec.record_id)
            if rec_instance:
                rec.record_name = rec_instance.display_name


class RecordMergeMixinFieldLine(models.AbstractModel):
    _name = 'record.merge.mixin.field.line'

    merge_id = fields.Many2one('record.merge.mixin', string="Merge")
    field_id = fields.Many2one('ir.model.fields', string="Field")
    model_id = fields.Many2one('ir.model', string="Model", related="field_id.model_id")
    to_merge = fields.Boolean(string="Merge", default=True)
    # TODO: add count of appearences with different values


class RecordMergeConsolidateField(models.Model):
    _name = 'record.merge.consolidate.field'
    _description = 'Fields to consolidate'
    _inherit = ['record.merge.mixin.field.line']

    field_id = fields.Many2one(
        domain="[('ttype', '!=', 'one2many'),"
               " ('related', '=', False),"
               " ('compute', '=', False)]")


class RecordMergeFkField(models.Model):
    _name = 'record.merge.fk.field'
    _description = 'Fks fields to merge'
    _inherit = ['record.merge.mixin.field.line']

    field_id = fields.Many2one(
        domain="[('ttype', '=', 'many2one')]")
    table = fields.Char(string="DB table")
    column = fields.Char(string="DB column")


class RecordMergeRefField(models.Model):
    _name = 'record.merge.ref.field'
    _description = 'Reference fields to merge'
    _inherit = ['record.merge.mixin.field.line']


class RecordMergeNonrelField(models.Model):
    _name = 'record.merge.nonrel.field'
    _description = 'Non-relational fields to merge'
    _inherit = ['record.merge.mixin.field.line']

    model_field_id = fields.Many2one('ir.model.fields', string="Field")


class RecordMergeRecField(models.Model):
    _name = 'record.merge.rec.field'
    _description = 'Fields to recompute'
    _inherit = ['record.merge.mixin.field.line']

    to_merge = fields.Boolean(string="To recompute")


