# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class MassSortConfigLine(models.Model):
    _name = 'mass.sort.config.line'
    _order = 'config_id, sequence, id'

    sequence = fields.Integer(string='Sequence', required=True, default=1)

    config_id = fields.Many2one(
        comodel_name='mass.sort.config', string='Wizard')

    field_id = fields.Many2one(
        comodel_name='ir.model.fields', string='Field', required=True,
        domain="[('model', '=', parent.one2many_model)]")

    desc = fields.Boolean(string='Inverse Order')

    # Constraint Section
    @api.constrains('field_id', 'config_id')
    def _check_field_id(self):
        for line in self:
            if line.field_id.model != line.config_id.one2many_model:
                raise ValidationError(_(
                    "The selected criteria '%s' must belong to the model of"
                    " the Field to Sort.") % (line.field_id.field_description))
