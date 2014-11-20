# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
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
###############################################################################

{
    "name": "Export Documents from database",
    "summary": "Export Existing Documents from Database to File System",
    "version": "1.0",
    "author": "Julius Network Solutions",
    "website": "http://julius.fr",
    "category": "Tools",
    "depends": [
        "document",
    ],
    "description": """
Add a Button to export existing documents from database to File System
======================================================================


* Make sure you've correctly defined the filestore in your database:
    * "Settings > Parameters > System Parameters":
        * "key": "ir_attachment.location"
        * "value": "file:///filestore"

* Go to your document list, select all the documents you want to extract.
* Click on "More > Documents Export"
    """,
    "data": [
        'view/view.xml',
        'view/action.xml',
        'data/ir_values.xml',
    ],
}
