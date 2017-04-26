# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class WizardModuleUninstallLine(models.TransientModel):
    _name = 'wizard.module.uninstall.line'

    LINE_TYPE_SELECTION = [
        ('model', 'Model'),
        ('field', 'Field'),
    ]

    DB_TYPE_SELECTION = [
        ('', 'Unknown Type'),
        ('r', 'Ordinary Table'),
        ('i', 'Index'),
        ('S', 'Sequence'),
        ('v', 'view'),
        ('c', 'Composite Type'),
        ('t', 'TOAST table'),
    ]

    wizard_id = fields.Many2one(
        comodel_name='wizard.module.uninstall', required=True)

    line_type = fields.Selection(
        selection=LINE_TYPE_SELECTION, required=True)

    model_id = fields.Many2one(comodel_name='ir.model', readonly=True)

    model_name = fields.Char(
        string='Model Name', related='model_id.model', readonly=True)

    table_size = fields.Integer(
        string='Table Size (KB)', compute='_compute_database',
        multi='database', store=True)

    index_size = fields.Integer(
        string='Indexes Size (KB)', compute='_compute_database',
        multi='database', store=True)

    db_type = fields.Selection(
        selection=DB_TYPE_SELECTION, compute='_compute_database',
        multi='database', store=True)

    db_size = fields.Integer(
        string='Total DB Size (KB)', compute='_compute_database',
        multi='database', store=True)

    model_row_qty = fields.Integer(
        string='Rows Quantity', compute='_compute_database', multi='database',
        store=True,
        help="The approximate value of the number of records in the database,"
        " based on the PostgreSQL column 'reltuples'.\n You should reindex"
        " your database, to have a more precise value\n\n"
        " 'REINDEX database your_database_name;'")

    field_id = fields.Many2one(comodel_name='ir.model.fields', readonly=True)

    field_name = fields.Char(
        string='Field Name', related='field_id.name', readonly=True)

    field_ttype = fields.Selection(
        string='Field Type', related='field_id.ttype', readonly=True)

    field_model_name = fields.Char(
        string='Field Model Name', related='field_id.model_id.model',
        readonly=True)

    @api.multi
    @api.depends('model_id', 'line_type')
    def _compute_database(self):
        table_names = []
        for line in self.filtered(lambda x: x.model_id):
            model_obj = self.env.registry.get(line.model_id.model, False)
            if model_obj:
                table_names.append(model_obj._table)
            else:
                # Try to guess table name, replacing "." by "_"
                table_names.append(line.model_id.model.replace('.', '_'))

        # Get Relation Informations
        req = (
            "SELECT"
            "   table_name,"
            "   row_qty,"
            "   db_type,"
            "   pg_table_size(table_name::regclass::oid) AS table_size,"
            "   pg_indexes_size(table_name::regclass::oid) AS index_size,"
            "   pg_total_relation_size(table_name::regclass::oid) AS db_size"
            " FROM ("
            "   SELECT"
            "       relname AS table_name,"
            "       reltuples AS row_qty,"
            "       relkind as db_type"
            "   FROM pg_class"
            "   WHERE relname IN %s) AS tmp;"
        )
        self.env.cr.execute(req, (tuple(table_names),))
        res = self.env.cr.fetchall()
        table_res = {x[0]: (x[1], x[2], x[3], x[4], x[5]) for x in res}
        for line in self:
            model_obj = self.env.registry.get(line.model_id.model, False)
            if model_obj:
                table_name = model_obj._table
            else:
                # Try to guess table name, replacing "." by "_"
                table_name = line.model_id.model.replace('.', '_')
            res = table_res.get(table_name, (0, '', 0, 0, 0))
            line.model_row_qty = res[0]
            line.db_type = res[1]
            line.table_size = res[2] / 1024
            line.index_size = res[3] / 1024
            line.db_size = res[4] / 1024
