# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#    Copyright (C) 2015 Agile Business Group <http://www.agilebg.com>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    "name": "Database Auto-Backup",
    "summary": "Backups database",
    "version": "8.0.1.0.0",
    "author": (
        "VanRoey.be - Yenthe Van Ginneken, Agile Business Group,"
        " Grupo ESOC Ingeniería de Servicios,"
        " Odoo Community Association (OCA)"
    ),
    'license': "AGPL-3",
    "website": "http://www.vanroey.be/applications/bedrijfsbeheer/odoo",
    "category": "Tools",
    "depends": ['email_template'],
    "demo": [],
    "data": [
        "data/backup_data.yml",
        "security/ir.model.access.csv",
        "view/db_backup_view.xml",
    ],
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": ["pysftp"],
    },
}
