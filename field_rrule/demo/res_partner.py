# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from dateutil.rrule import YEARLY, rrule
from openerp import api, fields, models
from openerp.addons.field_rrule.field_rrule import FieldRRule,\
    SerializableRRuleSet


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('rrule')
    def _compute_rrule_representation(self):
        for this in self:
            if not this.rrule:
                this.rrule_representation = 'You did not fill in rules yet'
                continue
            this.rrule_representation = 'First 5 dates: %s\n%s' % (
                ', '.join(map(str, this.rrule[:5])),
                this.rrule,
            )

    rrule = FieldRRule('RRule', default=SerializableRRuleSet(rrule(YEARLY)))
    rrule_representation = fields.Text(
        string='RRule representation', compute=_compute_rrule_representation)
