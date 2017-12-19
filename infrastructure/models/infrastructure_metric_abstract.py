# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureMetricAbstract(models.AbstractModel):

    _name = 'infrastructure.metric.abstract'
    _description = 'Infrastructure Abstract Metrics'
    _order = 'date desc'

    reference = fields.Reference([
        ('infrastructure.host', 'Host'),
        ('infrastructure.volume', 'Volume'),
        ('infrastructure.file.system', 'File System'),
    ],
        required=True,
        help='This is the object that the metric was taken from.',
    )
    date = fields.Datetime(
        default=fields.Datetime.now,
    )

    @api.model
    def create(self, values):
        return super(InfrastructureMetricAbstract, self).create(
            self._convert_reference(values),
        )

    @api.multi
    def write(self, values):
        return super(InfrastructureMetricAbstract, self).write(
            self._convert_reference(values),
        )

    @staticmethod
    def _convert_reference(values):
        if hasattr(values.get('reference'), 'id'):
            reference = values['reference']
            values['reference'] = '%s,%s' % (reference._name, reference.id)
        return values
