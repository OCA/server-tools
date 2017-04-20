# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class WizardModuleUninstallLine(models.TransientModel):
    _name = 'wizard.module.uninstall.line'

    TYPE_SELECTION = [
        ('model', 'Model'),
        ('field', 'Field'),
    ]

    wizard_id = fields.Many2one(
        comodel_name='wizard.module.uninstall', required=True)

    type = fields.Selection(
        selection=TYPE_SELECTION, required=True)

    model_id = fields.Many2one(comodel_name='ir.model', readonly=True)

    model_name = fields.Char(
        string='Model Name', related='model_id.model', readonly=True)

    model_row_qty = fields.Integer(
        string='Row Quantity', compute='_compute_model_row_qty')

    field_id = fields.Many2one(comodel_name='ir.model.fields', readonly=True)

    field_name = fields.Char(
        string='Field Name', related='field_id.name', readonly=True)

    field_ttype = fields.Selection(
        string='Field Type', related='field_id.ttype', readonly=True)

    field_model_name = fields.Char(
        string='Field Model Name', related='field_id.model_id.model',
        readonly=True)

    @api.multi
    @api.depends('model_id')
    def _compute_model_row_qty(self):
        table_names = []
        for line in self.filtered(lambda x: x.model_id):
            model_obj = self.env[line.model_id.model]
            table_names.append(model_obj._table)

        req = "SELECT relname AS table_name, reltuples AS row_qty"\
            " FROM pg_class C"\
            " LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)"\
            " WHERE "\
            " nspname NOT IN ('pg_catalog', 'information_schema')"\
            " AND relkind='r'"\
            " and relname in %s;"

        self.env.cr.execute(req, (tuple(table_names),))
        res = self.env.cr.fetchall()
        table_res = {x[0]: x[1] for x in res}

        for line in self:
            model_obj = self.env[line.model_id.model]
            line.model_row_qty = table_res.get(model_obj._table, 0)
