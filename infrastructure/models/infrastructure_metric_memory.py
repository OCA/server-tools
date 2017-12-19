# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureMetricMemory(models.Model):

    _name = 'infrastructure.metric.memory'
    _description = 'Infrastructure Memory Metrics'
    _inherit = 'infrastructure.metric.abstract'

    memory_active = fields.Float()
    memory_buffer = fields.Float()
    memory_cache = fields.Float()
    memory_inactive = fields.Float()
    memory_available = fields.Float()
    memory_free = fields.Float()
    memory_total = fields.Float()
    swap_cache = fields.Float()
    swap_free = fields.Float()
    swap_total = fields.Float()
    uom_id = fields.Many2one(
        string='Memory Units',
        comodel_name='product.uom',
        default=lambda s: s.env.ref(
            'product_uom_technology.product_uom_gib',
        ),
        domain="[('category_id.name', '=', 'Information')]",
        help='This unit represents all statistics for this record.',
    )
