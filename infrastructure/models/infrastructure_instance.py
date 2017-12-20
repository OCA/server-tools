# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureInstance(models.Model):

    _name = 'infrastructure.instance'
    _inherit = ['infrastructure.service.config',
                'infrastructure.service',
                ]
    _description = 'Infrastructure Instances'

    service_id = fields.Many2one(
        string='Service',
        comodel_name='infrastructure.service',
        required=True,
        ondelete='cascade',
    )
    mount_ids = fields.One2many(
        string='Mounts',
        comodel_name='infrastructure.volume.mount',
    )
