# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureOptionMount(models.Model):

    _name = 'infrastructure.option.system'
    _inherit = 'infrastructure.option'
    _description = 'Infrastructure System Options'

    value_2 = fields.Char(
        help='Sometimes there is a second value, such as permissions.',
    )
    value_2_join = fields.Char(
        default=':',
        help='If there is a ``value_2``, this will be used to join it with '
             'the existing values.',
    )

    @api.multi
    def name_get(self):
        results = []
        for record in self:
            name = '%s:%s' % (record.name, record.value)
            if record.value_2:
                name += '%s%s' % (record.value_2_join, record.value_2)
            results.append((record.id, name))
        return results
