# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureHost(models.Model):

    _name = 'infrastructure.host'
    _description = 'Infrastructure Hosts'

    name = fields.Char(
        string='Hostname',
    )
    description = fields.Char()
    environment_id = fields.Many2one(
        string='Environment',
        comodel_name='infrastructure.environment',
        required=True,
        ondelete='restrict',
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
    memory_metric_id = fields.Many2one(
        string='Latest Memory Metric',
        comodel_name='infrastructure.metric.memory',
        compute='_compute_memory_metric_id',
    )
    memory_metric_ids = fields.Many2many(
        string='Memory Metrics',
        comodel_name='infrastructure.metric.memory',
    )
    label_ids = fields.Many2many(
        string='Labels',
        comodel_name='infrastructure.option',
    )
    file_system_ids = fields.One2many(
        string='File Systems',
        comodel_name='infrastructure.file.system',
        inverse_name='host_id',
    )
    parent_id = fields.Many2one(
        string='Hypervisor',
        comodel_name=_name,
    )
    child_ids = fields.One2many(
        string='Virtual Machines',
        comodel_name=_name,
        inverse_name='parent_id',
    )

    @api.multi
    def _compute_memory_metric_id(self):
        for record in self:
            record.memory_metric_id = record.memory_metric_ids[:1].id
