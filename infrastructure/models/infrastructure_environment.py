# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureEnvironment(models.Model):

    _name = 'infrastructure.environment'
    _description = 'Infrastructure Environments'

    name = fields.Char(
        required=True,
    )
    description = fields.Char()
    state = fields.Selection([
        ('active', 'Active'),
        ('deactivated', 'Deactivated'),
    ],
        default='deactivated',
        required=True,
        readonly=True,
    )
    state_health = fields.Selection([
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
    ],
        default='unhealthy',
        required=True,
        readonly=True,
    )
    date_create = fields.Datetime(
        string='Create Date',
    )
    host_ids = fields.One2many(
        string='Hosts',
        comodel_name='infrastructure.host',
        inverse_name='environment_id',
    )
    connector_id = fields.Many2one(
        string='Connector',
        comodel_name='infrastructure.connector',
        required=True,
        ondelete='restrict',
    )
    company_ids = fields.Many2many(
        string='Companies',
        comodel_name='res.company',
        help='Users from these companies have access to the environment.',
    )
    domain = fields.Char(
        help='This is the base domain for the environment.',
    )
