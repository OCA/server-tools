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

from osv import fields, osv

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

    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'min': fields.float('Minimum', required=True),
        'max': fields.float('Maximum', size=50, required=True),
        'color': fields.char('Color (RGB code)', size=7, required=True),
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

class mgmtsystem_kpi_periodicity_uom(osv.osv):
    """
    Unit of Measure for Periodicity
    """
    _name = "mgmtsystem.kpi.periodicity.uom"
    _description = "Periodicity Unit of Measure"

    _columns = {
        'name': fields.char('Name', size=10, required=True),
    }

mgmtsystem_kpi_threshold()

class mgmtsystem_kpi(osv.osv):
    """
    Key Performance Indicators
    """
    _name = "mgmtsystem.kpi"
    _description = "Key Performance Indicator"
    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'description': fields.text('Description'),
        'category_id': fields.many2one('mgmtsystem.kpi.category','Category', required=True),
        'threshold_id': fields.many2one('mgmtsystem.kpi.threshold','Threshold', required=True),
        'periodicity': fields.integer('Periodicity'),
        'periodicity_uom': fields.many2one('mgmtsystem.kpi.periodicity.uom','Periodicity UoM', required=True),
        'value': fields.float('Value'),
    }

mgmtsystem_kpi()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
