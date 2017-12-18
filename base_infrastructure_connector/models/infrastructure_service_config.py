# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureServiceConfig(models.Model):

    _name = 'infrastructure.service.config'
    _description = 'Infrastructure Service Configuration'

    service_id = fields.Many2one(
        string='Service',
        comodel_name='infrastructure.service',
        required=True,
        ondelete='cascade',
    )
    # Instance config options
