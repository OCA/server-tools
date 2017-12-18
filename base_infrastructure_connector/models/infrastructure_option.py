# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureOption(models.Model):

    _name = 'infrastructure.option'
    _description = 'Infrastructure Options'

    name = fields.Char(
        required=True,
    )
    value = fields.Char(
        required=True,
    )

    @api.multi
    def name_get(self):
        return [
            (n.id, '%s: "%s"' % (n.name, n.value)) for n in self
        ]
