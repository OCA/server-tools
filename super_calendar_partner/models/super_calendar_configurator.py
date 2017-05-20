# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import _, api, exceptions, models


class SuperCalendarConfigurator(models.Model):
    _inherit = 'super.calendar.configurator'

    @api.multi
    def _get_record_values_from_line(self, line):
        res = super(
            SuperCalendarConfigurator, self
        )._get_record_values_from_line(line)
        for record in res:
            f_partner = line.partner_field_id.name
            if (f_partner and
                    record[f_partner]._model._name != 'res.partner'):
                raise exceptions.ValidationError(
                    _("The 'Partner' field of record %s (%s) "
                      "does not refer to res.partner")
                    % (res[record]['name'], line.name.model))
            res[record]['partner_id'] = (f_partner and
                                         record[f_partner].id)
        return res
