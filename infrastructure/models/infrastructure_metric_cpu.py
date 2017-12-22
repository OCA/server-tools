# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureMetricCpu(models.Model):

    _name = 'infrastructure.metric.cpu'
    _inherit = 'infrastructure.metric.abstract'
    _description = 'Infrastructure CPU Metrics'

    name = fields.Char()
    core_metric_ids = fields.One2many(
        string='Core Metrics',
        comodel_name='infrastructure.metric.cpu.core',
        inverse_name='cpu_metric_id',
        readonly=True,
    )
    load_one = fields.Float(
        readonly=True,
        help='Load average for past minute.',
    )
    load_five = fields.Float(
        readonly=True,
        help='Load average for past five minutes.',
    )
    load_fifteen = fields.Float(
        readonly=True,
        help='Load average for past fifteen minutes.',
    )
    core_count = fields.Integer(
        readonly=True,
    )
    frequency = fields.Float(
        readonly=True,
    )
    frequency_uom_id = fields.Many2one(
        string='Frequency Units',
        comodel_name='product.uom',
        readonly=True,
        domain="[('category_id.name', '=', 'Frequency')]",
    )

    @api.multi
    def name_get(self):
        names = []
        for record in self:
            name = '%s, %s, %s' % (
                record.load_one, record.load_five, record.load_fifteen,
            )
            names.append((record.id, name))
        return names
