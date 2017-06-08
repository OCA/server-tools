# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2015 FactorLibre (<http://www.factorlibre.com>)
#                       Ismael Calvo <ismael.calvo@factorlibre.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
import logging
from mako.template import Template
from datetime import datetime
from openerp import tools
from openerp.tools.safe_eval import safe_eval


def _models_get(self, cr, uid, context=None):
    obj = self.pool.get('ir.model')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['model', 'name'], context)
    return [(r['model'], r['name']) for r in res]


class super_calendar_configurator(orm.Model):
    _logger = logging.getLogger('super.calendar')
    _name = 'super.calendar.configurator'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'line_ids': fields.one2many('super.calendar.configurator.line',
                                    'configurator_id', 'Lines'),
    }

    def generate_calendar_records(self, cr, uid, ids, context=None):
        configurator_ids = self.search(cr, uid, [])
        super_calendar_pool = self.pool.get('super.calendar')

        # removing old records
        super_calendar_ids = super_calendar_pool.search(cr, uid, [],
                                                        context=context)
        super_calendar_pool.unlink(cr, uid,
                                   super_calendar_ids,
                                   context=context)

        for configurator in self.browse(cr, uid, configurator_ids, context):
            for line in configurator.line_ids:
                current_pool = self.pool.get(line.name.model)
                current_record_ids = current_pool.search(
                    cr,
                    uid,
                    line.domain and safe_eval(line.domain) or [],
                    context=context)

                for current_record_id in current_record_ids:
                    values = self._generate_record_from_line(cr, uid,
                                                             configurator,
                                                             line,
                                                             current_record_id,
                                                             context)
                    super_calendar_pool.create(cr, uid, values,
                                               context=context)
        self._logger.info('Calendar generated')
        return True

    def _generate_record_from_line(self, cr, uid, configurator, line,
                                   current_record_id, context):
        current_pool = self.pool.get(line.name.model)

        record = current_pool.browse(cr, uid,
                                     current_record_id,
                                     context=context)
        if line.user_field_id and \
           record[line.user_field_id.name] and \
           record[line.user_field_id.name]._table_name != 'res.users':
            raise orm.except_orm(
                _('Error'),
                _("The 'User' field of record %s (%s) "
                  "does not refer to res.users")
                % (record[line.description_field_id.name],
                   line.name.model))

        if (((line.description_field_id and
              record[line.description_field_id.name]) or
                line.description_code) and
                record[line.date_start_field_id.name]):
            duration = False
            if (not line.duration_field_id and
                    line.date_stop_field_id and
                    record[line.date_start_field_id.name] and
                    record[line.date_stop_field_id.name]):
                date_start = datetime.strptime(
                    record[line.date_start_field_id.name],
                    tools.DEFAULT_SERVER_DATETIME_FORMAT
                )
                date_stop = datetime.strptime(
                    record[line.date_stop_field_id.name],
                    tools.DEFAULT_SERVER_DATETIME_FORMAT
                )
                duration = (date_stop - date_start).total_seconds() / 3600
            elif line.duration_field_id:
                duration = record[line.duration_field_id.name]
            if line.description_type != 'code':
                name = record[line.description_field_id.name]
            else:
                parse_dict = {'o': record}
                mytemplate = Template(line.description_code)
                name = mytemplate.render(**parse_dict)
            return {
                'name': name,
                'model_description': line.description,
                'date_start': record[line.date_start_field_id.name],
                'duration': duration,
                'user_id': (
                    line.user_field_id and
                    record[line.user_field_id.name] and
                    record[line.user_field_id.name].id or
                    False
                ),
                'configurator_id': configurator.id,
                'res_id': line.name.model + ',' + str(record['id']),
                'model_id': line.name.id,
            }
        return {}


class super_calendar_configurator_line(orm.Model):
    _name = 'super.calendar.configurator.line'
    _columns = {
        'name': fields.many2one('ir.model', 'Model', required=True),
        'description': fields.char('Description', size=128, required=True),
        'domain': fields.char('Domain', size=512),
        'configurator_id': fields.many2one('super.calendar.configurator',
                                           'Configurator'),
        'description_type': fields.selection([
            ('field', 'Field'),
            ('code', 'Code'),
        ], string="Description Type"),
        'description_field_id': fields.many2one(
            'ir.model.fields', 'Description field',
            domain="[('model_id', '=', name),('ttype', '=', 'char')]"),
        'description_code': fields.text(
            'Description field',
            help="Use '${o}' to refer to the involved object. "
                 "E.g.: '${o.project_id.name}'"),
        'date_start_field_id': fields.many2one(
            'ir.model.fields', 'Start date field',
            domain="['&','|',('ttype', '=', 'datetime'),"
                   "('ttype', '=', 'date'),"
                   "('model_id', '=', name)]",
            required=True),
        'date_stop_field_id': fields.many2one(
            'ir.model.fields', 'End date field',
            domain="['&',('ttype', '=', 'datetime'),('model_id', '=', name)]"
        ),
        'duration_field_id': fields.many2one(
            'ir.model.fields', 'Duration field',
            domain="['&',('ttype', '=', 'float'),('model_id', '=', name)]"),
        'user_field_id': fields.many2one(
            'ir.model.fields', 'User field',
            domain="['&',('ttype', '=', 'many2one'),('model_id', '=', name)]"),
    }


class super_calendar(orm.Model):
    _name = 'super.calendar'
    _columns = {
        'name': fields.char('Description', size=512, required=True),
        'model_description': fields.char('Model Description',
                                         size=128,
                                         required=True),
        'date_start': fields.datetime('Start date', required=True),
        'duration': fields.float('Duration'),
        'user_id': fields.many2one('res.users', 'User'),
        'configurator_id': fields.many2one('super.calendar.configurator',
                                           'Configurator'),
        'res_id': fields.reference('Resource',
                                   selection=_models_get,
                                   size=128),
        'model_id': fields.many2one('ir.model', 'Model'),
    }
