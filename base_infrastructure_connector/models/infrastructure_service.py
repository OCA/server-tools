# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureService(models.Model):

    _name = 'infrastructure.service'
    _description = 'Infrastructure Services'

    name = fields.Char(
        required=True,
    )
    description = fields.Char()
    state = fields.Selection([
        # @TODO: this
    ])
    date_create = fields.Datetime(
        string='Creation Date',
        default=fields.Datetime.now,
    )
    scale_current = fields.Integer()
    scale_max = fields.Integer()
    fqdn = fields.Char()
    state_health = fields.Selection([
        # @TODO: Centralize from volumes
    ])
    instance_ids = fields.One2many(
        string='Instances',
        comodel_name='infrastructure.instance',
    )
    config_id = fields.Many2one(
        string='Configuration',
        comodel_name='infrastructure.service.config',
    )

