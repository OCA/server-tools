# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    "name": "Generate Docs of Modules",
    "version": "8.0.1.0.0",
    "category": "Tools",
    "summary": "Modules Technical Guides in RST and Relationship Graphs",
    "website": "https://odoo-community.org/",
    "author": "OpenERP SA,Odoo Community Association (OCA)",
    "contributors": [
        "OpenERP SA <http://www.odoo.com>",
        "Matjaž Mozetič <m.mozetic@matmoz.si>",
    ],
    "license": "AGPL-3",
    "depends": ["base"],
    "external_dependencies": {
        'python': [
            'pydot',
        ],
    },
    "data": [
        "base_module_doc_rst_view.xml",
        "wizard/generate_relation_graph_view.xml",
        "wizard/tech_guide_rst_view.xml",
        "module_report.xml",
    ],
    "demo": [],
    "installable": False,
}
