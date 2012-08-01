# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from dateutil.relativedelta import relativedelta
from datetime import datetime
from osv import fields, osv
import time

class mgmtsystem_kpi_category(osv.osv):
    """
    KPI Category
    """
    _name = "mgmtsystem.kpi.category"
    _description = "KPI Category"
    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'description': fields.text('Description')
    }

mgmtsystem_kpi_category()

class mgmtsystem_kpi_threshold_range(osv.osv):
    """
    KPI Threshold Range
    """
    _name = "mgmtsystem.kpi.threshold.range"
    _description = "KPI Threshold Range"

    def _compute_min_value(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr, uid, ids):
            value = 0
            if obj.min_type == 'sql':
                cr.execute(obj.min_code)
                value = cr.dictfetchone()['value']
            elif obj.min_type == 'python':
                value = eval(obj.min_code)
            else:
                value = obj.min_fixed_value

            result[obj.id] = value

        return result

    def _compute_max_value(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr, uid, ids):
            value = 0
            if obj.max_type == 'sql':
                cr.execute(obj.max_code)
                value = cr.dictfetchone()['value']
            elif obj.max_type == 'python':
                value = eval(obj.max_code)
            else:
                value = obj.max_fixed_value

            result[obj.id] = value

        return result

    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'min_type': fields.selection((('static','Fixed value'), ('python','Python Code'), ('sql', 'SQL Query')), 'Min Type', required=True),
        'min_value': fields.function(_compute_min_value, string='Minimum', type='float'),
        'min_fixed_value': fields.float('Minimum'),
        'min_code': fields.text('Minimum Computation Code'),
        'max_type': fields.selection((('static','Fixed value'), ('python','Python Code'), ('sql', 'SQL Query')), 'Max Type', required=True),
        'max_value': fields.function(_compute_max_value, string='Maximum', type='float'),
        'max_fixed_value': fields.float('Maximum'),
        'max_code': fields.text('Maximum Computation Code'),
        'color': fields.char('Color', help='RGB code with #', size=7, required=True),
    }

mgmtsystem_kpi_threshold_range()

class mgmtsystem_kpi_threshold(osv.osv):
    """
    KPI Threshold
    """
    _name = "mgmtsystem.kpi.threshold"
    _description = "KPI Threshold"

    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'range_ids': fields.many2many('mgmtsystem.kpi.threshold.range','mgmtsystem_kpi_threshold_range_rel', 'threshold_id', 'range_id', 'Range', required=True),
    }

mgmtsystem_kpi_threshold()

class mgmtsystem_kpi_history(osv.osv):
    """
    History of the KPI
    """
    _name = "mgmtsystem.kpi.history"
    _description = "History of the KPI"

    _columns = {
        'name': fields.char('Name', size=150, required=True),
        'kpi_id': fields.many2one('mgmtsystem.kpi', 'KPI', required=True),
        'date': fields.datetime('Execution Date', required=True, readonly=True),
        'value': fields.float('Value', required=True, readonly=True),
    }

    _defaults = {
        'name': lambda *a: time.strftime('%d %B %Y'),
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    _order = "date desc" 

mgmtsystem_kpi_threshold()

class mgmtsystem_kpi(osv.osv):
    """
    Key Performance Indicators
    """
    _name = "mgmtsystem.kpi"
    _description = "Key Performance Indicator"

    def _display_last_kpi_value(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        
        result = {}
        for obj in self.browse(cr, uid, ids):
            if obj.history_ids:
                result[obj.id] = obj.history_ids[0].value
            else:
                result[obj.id] = 0

        return result

    def compute_kpi_value(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        kpi_value = 0 

        for obj in self.browse(cr, uid, ids):       
            kpi_value = 0 
            if obj.kpi_type == 'sql':
                cr.execute(obj.kpi_code)
                kpi_value = cr.dictfetchone()['value']
            elif obj.kpi_type == 'python':
                kpi_value = eval(obj.kpi_code)
        
            values = {
	        'kpi_id': obj.id,
                'value': kpi_value,
	    }

            history_obj = self.pool.get('mgmtsystem.kpi.history')
            history_id = history_obj.create(cr, uid, values, context=context)
            obj.history_ids.append(history_id)

        return True

    def update_next_execution_date(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        for obj in self.browse(cr, uid, ids):
            if obj.periodicity_uom == 'hour':
                new_date = datetime.now() + relativedelta( hours = +obj.periodicity )
            elif obj.periodicity_uom == 'day': 
                new_date = datetime.now() + relativedelta( days = +obj.periodicity )
            elif obj.periodicity_uom == 'week': 
                new_date = datetime.now() + relativedelta( weeks = +obj.periodicity )
            elif obj.periodicity_uom == 'month': 
                new_date = datetime.now() + relativedelta( months = +obj.periodicity )

            values = {
                'next_execution_date': new_date.strftime('%Y-%m-%d %H:%M:%S'),
            }

            obj.write(values)

        return True

    # Method called by the scheduler
    def update_kpi_value(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        if not ids:
            filters = ['&', '|', ('active', '=', True), ('next_execution_date', '<=', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), ('next_execution_date', '=', False)]
            if 'filters' in context:
                filters.extend(context['filters'])
            ids = self.search(cr, uid, filters, context=context)
        res = None

        try:
            res = self.compute_kpi_value(cr, uid, ids, context=context)
            self.update_next_execution_date(cr, uid, ids, context=context)
        except Exception:
            _logger.exception("Failed updating KPI values")
        
        return res

    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'description': fields.text('Description'),
        'category_id': fields.many2one('mgmtsystem.kpi.category','Category', required=True),
        'threshold_id': fields.many2one('mgmtsystem.kpi.threshold','Threshold', required=True),
        'periodicity': fields.integer('Periodicity'),
        'periodicity_uom': fields.selection((('hour','Hour'), ('day','Day'), ('week','Week'), ('month','Month')), 'Periodicity UoM', required=True),
        'next_execution_date': fields.datetime('Next execution date', readonly=True),
        'value': fields.function(_display_last_kpi_value, string='Value', type='float'),
        'kpi_type': fields.selection((('sql','SQL'), ('python','Python')),'KPI Computation Type'),
        'kpi_code': fields.text('KPI Code', help='SQL code must return the result as \'value\' (i.e. \'SELECT 5 AS value\').'),
        'history_ids': fields.one2many('mgmtsystem.kpi.history', 'kpi_id', 'History'),
        'active': fields.boolean('Active', help="Only active KPIs will be updated by the scheduler based on the periodicity configuration."),
    }

    _defaults = {
        'active': True,
        'periodicity': 1,
        'periodicity_uom': 'day',
    }

mgmtsystem_kpi()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
