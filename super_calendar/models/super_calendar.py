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

from openerp import models, fields, api
from openerp.tools.translate import _
from mako.template import Template
from datetime import datetime
from openerp import tools
from openerp.tools.safe_eval import safe_eval
import logging


def _models_get(self):
    model_obj = self.env['ir.model']
    model_ids = model_obj.search([])
    return [(model.model, model.name) for model in model_ids]


class SuperCalendarConfigurator(models.Model):
    _logger = logging.getLogger(__name__)
    _name = 'super.calendar.configurator'

    name = fields.Char(
        string='Name',
        size=64,
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name='super.calendar.configurator.line',
        inverse_name='configurator_id',
        string='Lines',
    )

    def _clear_super_calendar_records(self):
        """ Remove old super_calendar records """
        super_calendar_pool = self.env['super.calendar']
        super_calendar_ids = super_calendar_pool.search([])
        super_calendar_ids.unlink()

    @api.multi
    def generate_calendar_records(self):
        """ At every CRON execution, every 'super calendar' data is deleted
        and regenerated again. """

        # Remove old records
        self._clear_super_calendar_records()

        # Rebuild all calendar records
        configurator_ids = self.search([])
        for configurator in configurator_ids:
            for line in configurator.line_ids:
                self._generate_record_from_line(configurator, line)
        self._logger.info('Calendar generated')
        return True

    @api.multi
    def _generate_record_from_line(self, configurator, line):
        super_calendar_pool = self.env['super.calendar']
        values = self._get_record_values_from_line(configurator, line)
        for record in values:
            super_calendar_pool.create(values[record])

    @api.multi
    def _get_record_values_from_line(self, configurator, line):
        res = {}
        current_pool = self.env[line.name.model]
        domain = line.domain and safe_eval(line.domain) or []
        current_record_ids = current_pool.search(domain)
        for cur_rec in current_record_ids:
            f_user = line.user_field_id and line.user_field_id.name
            f_descr = (line.description_field_id and
                       line.description_field_id.name)
            f_date_start = (line.date_start_field_id and
                            line.date_start_field_id.name)
            f_date_stop = (line.date_stop_field_id and
                           line.date_stop_field_id.name)
            f_duration = (line.duration_field_id and
                          line.duration_field_id.name)
            if (f_user and
                    cur_rec[f_user] and
                    cur_rec[f_user]._model._name != 'res.users'):
                raise Exception(
                    _('Error'),
                    _("The 'User' field of record %s (%s) "
                      "does not refer to res.users")
                    % (cur_rec[f_descr], line.name.model))

            if (((f_descr and cur_rec[f_descr]) or
                    line.description_code) and
                    cur_rec[f_date_start]):
                duration = False
                if (not line.duration_field_id and
                        line.date_stop_field_id and
                        cur_rec[f_date_start] and
                        cur_rec[f_date_stop]):
                    date_start = datetime.strptime(
                        cur_rec[f_date_start],
                        tools.DEFAULT_SERVER_DATETIME_FORMAT
                    )
                    date_stop = datetime.strptime(
                        cur_rec[f_date_stop],
                        tools.DEFAULT_SERVER_DATETIME_FORMAT
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

                super_calendar_values = {
                    'name': name,
                    'date_start': cur_rec[f_date_start],
                    'duration': duration,
                    'user_id': (
                        f_user and
                        cur_rec[f_user] and
                        cur_rec[f_user].id or
                        False
                    ),
                    'configurator_id': configurator.id,
                    'res_id': line.name.model+','+str(cur_rec['id']),
                    'model_id': line.name.id,
                }
                res[cur_rec] = super_calendar_values
        return res


class SuperCalendarConfiguratorLine(models.Model):
    _name = 'super.calendar.configurator.line'

    name = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
    )
    domain = fields.Char(
        string='Domain',
        size=512,
    )
    configurator_id = fields.Many2one(
        comodel_name='super.calendar.configurator',
        string='Configurator',
    )
    description_type = fields.Selection(
        [('field', 'Field'),
         ('code', 'Code')],
        string="Description Type",
    )
    description_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Description field',
        domain=("['&','|',('ttype', '=', 'char'),('ttype', '=', 'text'),"
                "('model_id', '=', name)]"),
    )
    description_code = fields.Text(
        string='Description field',
        help=("Use '${o}' to refer to the involved object. "
              "E.g.: '${o.project_id.name}'"),
    )
    date_start_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Start date field',
        domain=("['&','|',('ttype', '=', 'datetime'),('ttype', '=', 'date'),"
                "('model_id', '=', name)]"),
        required=True,
    )
    date_stop_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='End date field',
        domain="['&',('ttype', '=', 'datetime'),('model_id', '=', name)]"
    )
    duration_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Duration field',
        domain="['&',('ttype', '=', 'float'), ('model_id', '=', name)]",
    )
    user_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='User field',
        domain="['&', ('ttype', '=', 'many2one'), ('model_id', '=', name)]",
    )


class SuperCalendar(models.Model):
    _name = 'super.calendar'

    name = fields.Char(
        string='Description',
        size=512,
        required=True,
    )
    date_start = fields.Datetime(
        string='Start date',
        required=True,
    )
    duration = fields.Float(
        string='Duration'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
    )
    configurator_id = fields.Many2one(
        comodel_name='super.calendar.configurator',
        string='Configurator',
    )
    res_id = fields.Reference(
        selection=_models_get,
        string='Resource',
        size=128,
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
    )
