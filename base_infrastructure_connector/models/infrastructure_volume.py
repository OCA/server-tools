# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureVolume(models.Model):

    _name = 'infrastructure.volume'
    _description = 'Infrastructure Volumes'

    name = fields.Char(
        required=True,
    )
    external_name = fields.Char(
        help='This is the name of the volume according to the volume driver.',
    )
    state = fields.Selection([
        ('active', 'Active'),
        ('disconnected', 'Disconnected'),
        ('inactive', 'Inactive'),
        ('reconnecting', 'Reconnecting'),
        ('purged', 'Purged'),
    ],
        default='inactive',
        required=True,
    )
    access_mode = fields.Char()
    driver = fields.Char()
    driver_option_ids = fields.Many2many(
        string='Driver Options',
        comodel_name='infrastructure.option',
    )
    host_id = fields.Many2one(
        string='Host',
        comodel_name='infrastructure.host',
        required=True,
    )
    is_host_path = fields.Boolean(
        help='This indicates that the volume is located directly on the host.',
    )
    mount_ids = fields.One2many(
        string='Mounts',
        comodel_name='infrastructure.volume.mount',
        inverse_name='volume_id',
    )
    capacity = fields.Float()
    capacity_uom_id = fields.Many2one(
        string='Capacity Units',
        comodel_name='product.uom',
        default=lambda s: s.env.ref(
            'product_uom_technology.product_uom_gib',
        ),
        domain="[('category_id.name', '=', 'Information')]",
    )

    @api.multi
    def name_get(self):
        return [
            (n.id, '%s: "%s"' % (n.name, n.value)) for n in self
        ]
