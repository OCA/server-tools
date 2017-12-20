# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureConnector(models.Model):

    _name = 'infrastructure.connector'
    _description = 'Infrastructure Connector Adapter'
    _inherit = 'external.system.adapter'
    _order = 'sequence'

    sequence = fields.Integer(
        required=True,
        default=50,
    )
    interface_type = fields.Selection(
        selection='_get_interface_types',
        required=True,
    )

    @api.model
    def _get_interface_types(self):
        """Child modules should add themselves to these selection values."""
        return []
