# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class InfrastructureVolumeMount(models.Model):

    _name = 'infrastructure.volume.mount'
    _description = 'Infrastructure Volume Mount'

    instance_id = fields.Many2one(
        string='Instance',
        comodel_name='infrastructure.instance',
        required=True,
        ondelete='cascade',
    )
    volume_id = fields.Many2one(
        string='Volume',
        comodel_name='infrastructure.volume',
        required=True,
        ondelete='restrict',
    )
    path = fields.Char(
        required=True,
    )
    is_read_only = fields.Boolean(
        help='Is this volume mounted as read only?',
    )
    size = fields.Float()
    size_uom_id = fields.Many2one(
        string='Size Units',
        comodel_name='product.uom',
        default=lambda s: s.env.ref(
            'product_uom_technology.product_uom_gib',
        ),
        domain="[('category_id.name', '=', 'Information')]",
    )
