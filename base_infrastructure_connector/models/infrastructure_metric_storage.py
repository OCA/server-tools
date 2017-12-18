# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureMetricStorage(models.Model):

    _name = 'infrastructure.metric.storage'
    _description = 'Infrastructure Storage Metrics'
    _inherit = 'infrastructure.metric.abstract'

    uom_id = fields.Many2one(
        string='Memory Units',
        comodel_name='product.uom',
        default=lambda s: s.env.ref(
            'product_uom_technology.product_uom_gib',
        ),
        domain="[('category_id.name', '=', 'Information')]",
        help='This unit represents all statistics for this record.',
    )
    free = fields.Float()
    used = fields.Float()
    total = fields.Float()
    percent_used = fields.Float(
        compute='_compute_percents',
    )
    percent_free = fields.Float(
        compute='_compute_percents',
    )

    @api.multi
    @api.depends('free', 'total', 'used')
    def _compute_percents(self):
        for record in self:
            record.percent_free = record.free / record.total
            record.percent_used = record.used / record.total
