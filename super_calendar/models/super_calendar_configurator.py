# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2012      Agile Business Group sagl (<http://www.agilebg.com>)
#        (c) 2012      Domsense srl (<http://www.domsense.com>)
#        (c) 2015      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#        (c) 2015      Savoir-faire Linux <http://www.savoirfairelinux.com>)
#                      Agathe Mollé <agathe.molle@savoirfairelinux.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
##############################################################################

import logging
from datetime import datetime
from pytz import timezone, utc
from mako.template import Template
from openerp import _, api, exceptions, fields, models, tools
from openerp.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class SuperCalendarConfigurator(models.Model):
    _name = 'super.calendar.configurator'

    name = fields.Char(
        string='Name',
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name='super.calendar.configurator.line',
        inverse_name='configurator_id',
        string='Lines',
    )

    def _clear_super_calendar_records(self):
        """
        Remove old super_calendar records
        """
        super_calendar_pool = self.env['super.calendar']
        super_calendar_list = super_calendar_pool.search([])
        super_calendar_list.unlink()

    @api.multi
    def generate_calendar_records(self):
        """
        At every CRON execution, every 'super calendar' data is deleted and
        regenerated again.
        """

        # Remove old records
        self._clear_super_calendar_records()

        # Rebuild all calendar records
        configurator_list = self.search([])
        for configurator in configurator_list:
            for line in configurator.line_ids:
                configurator._generate_record_from_line(line)
        _logger.info('Calendar generated')
        return True

    @api.multi
    def _generate_record_from_line(self, line):
        """
        Create super_calendar records from super_calendar_configurator_line
        objects.
        """
        super_calendar_pool = self.env['super.calendar']
        values = self._get_record_values_from_line(line)
        for record in values:
            super_calendar_pool.create(values[record])

    @api.multi
    def _get_record_values_from_line(self, line):
        """
        Get super_calendar fields values from super_calendar_configurator_line
        objects.
        Check if the User value is a res.users.
        """
        res = {}
        current_pool = self.env[line.name.model]
        domain = line.domain and safe_eval(line.domain) or []
        current_record_list = current_pool.search(domain)
        for cur_rec in current_record_list:
            f_user = line.user_field_id.name
            f_descr = line.description_field_id.name
            f_date_start = line.date_start_field_id.name
            f_date_stop = line.date_stop_field_id.name
            f_duration = line.duration_field_id.name

            # Check if f_user refer to a res.users
            if (f_user and cur_rec[f_user] and
                    cur_rec[f_user]._model._name != 'res.users'):
                raise exceptions.ValidationError(
                    _("The 'User' field of record %s (%s) "
                      "does not refer to res.users")
                    % (cur_rec[f_descr], line.name.model))

            if ((cur_rec[f_descr] or line.description_code) and
                    cur_rec[f_date_start]):
                duration = False

                if line.date_start_field_id.ttype == 'date':
                    date_format = tools.DEFAULT_SERVER_DATE_FORMAT
                else:
                    date_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
                date_start = datetime.strptime(
                    cur_rec[f_date_start], date_format
                )

                if (not line.duration_field_id and
                        line.date_stop_field_id and
                        cur_rec[f_date_start] and
                        cur_rec[f_date_stop]):
                    if line.date_stop_field_id.ttype == 'date':
                        date_format = tools.DEFAULT_SERVER_DATE_FORMAT
                    else:
                        date_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
                    date_stop = datetime.strptime(
                        cur_rec[f_date_stop], date_format
                    )
                    date_diff = (date_stop - date_start)
                    duration = date_diff.total_seconds() / 3600

                elif line.duration_field_id:
                    duration = cur_rec[f_duration]

                if line.description_type != 'code':
                    name = cur_rec[f_descr]
                else:
                    parse_dict = {'o': cur_rec}
                    mytemplate = Template(line.description_code)
                    name = mytemplate.render(**parse_dict)

                # Convert date_start to UTC timezone if it is a date field
                # in order to be stored in UTC in the database
                if line.date_start_field_id.ttype == 'date':
                    tz = timezone(self._context.get('tz')
                                  or self.env.user.tz
                                  or 'UTC')
                    local_date_start = tz.localize(date_start)
                    utc_date_start = local_date_start.astimezone(utc)
                    date_start = utc_date_start
                date_start = datetime.strftime(
                    date_start,
                    tools.DEFAULT_SERVER_DATETIME_FORMAT
                )

                super_calendar_values = {
                    'name': name,
                    'date_start': date_start,
                    'duration': duration,
                    'user_id': (f_user and cur_rec[f_user].id),
                    'configurator_id': self.id,
                    'res_id': line.name.model + ',' + str(cur_rec['id']),
                    'model_id': line.name.id,
                }
                res[cur_rec] = super_calendar_values
        return res
