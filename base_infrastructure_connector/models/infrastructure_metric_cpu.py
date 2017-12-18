# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureMetricCpu(models.Model):

    _name = 'infrastructure.metric.cpu'
    _description = 'Infrastructure CPU Metrics'
    _inherit = 'infrastructure.metric.abstract'

    name = fields.Char()
    core_metric_ids = fields.One2many(
        string='Core Metrics',
        comodel_name='infrastructure.cpu.core',
        inverse_name='cpu_metric_id',
    )
    load_one = fields.Float(
        help='Load average for past minute.',
    )
    load_five = fields.Float(
        help='Load average for past five minutes.',
    )
    load_fifteen = fields.Float(
        help='Load average for past fifteen minutes.',
    )
    core_count = fields.Integer()
    frequency = fields.Float()
    frequency_uom_id = fields.Many2one(
        string='Frequency Units',
        comodel_name='product.uom',
        domain="[('category_id.name', '=', 'Frequency')]",
    )
