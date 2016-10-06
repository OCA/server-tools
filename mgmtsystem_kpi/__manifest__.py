# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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
{
    "name": "Key Performance Indicator",
    "version": "7.0.1.1.1",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "category": "Management System",
    "complexity": "normal",
    "description": """\
This module provides the basis for creating key performance indicators,
including static and dynamic thresholds (SQL query or Python code),
on local and remote data sources.

The module also provides the mecanism to update KPIs automatically.
A scheduler is executed every hour and updates the KPI values, based
on the periodicity of each KPI. KPI computation can also be done
manually.

A threshold is a list of ranges and a range is:
 * a name (like Good, Warning, Bad)
 * a minimum value (fixed, sql query or python code)
 * a maximum value (fixed, sql query or python code)
 * color (RGB code like #00FF00 for green, #FFA500 for orange,
   #FF0000 for red)

This module depends on:
 * base_external_dbsource (available in lp:openobject-extension)
 * web_color (available in lp:web-addons)
    """,
    "depends": [
        'mgmtsystem',
        'base_external_dbsource',
        'web_color',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/mgmtsystem_kpi_security.xml',
        'mgmtsystem_kpi_view.xml',
    ],
    "images": [
        "images/kpi_definition.png",
        "images/kpi_computation.png",
        "images/kpi_threshold.png",
        "images/kpi_range.png",
    ],
    "demo": [],
    "test": [],
    'installable': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
