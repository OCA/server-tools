# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureMetricMemory(models.Model):

    _name = 'infrastructure.metric.memory'
    _description = 'Infrastructure Memory Metrics'
    _inherit = 'infrastructure.metric.abstract'

    memory_free = fields.Float(
        readonly=True,
    )
    memory_cache = fields.Float(
        readonly=True,
    )
    memory_used = fields.Float(
        readonly=True,
    )
    memory_total = fields.Float(
        readonly=True,
    )
    swap_cache = fields.Float(
        readonly=True,
    )
    swap_free = fields.Float(
        readonly=True,
    )
    swap_total = fields.Float(
        readonly=True,
    )
    uom_id = fields.Many2one(
        string='Memory Units',
        comodel_name='product.uom',
        readonly=True,
        default=lambda s: s.env.ref(
            'product_uom_technology.product_uom_gib',
        ),
        domain="[('category_id.name', '=', 'Information')]",
        help='This unit represents all statistics for this record.',
    )

    @api.multi
    def name_get(self):
        names = []
        for record in self:
            name = '%s total, %s free, %s used, %s buff/cache' % (
                record.memory_total,
                record.memory_free,
                record.memory_used,
                record.memory_cache,
            )
            names.append((record.id, name))
        return names
