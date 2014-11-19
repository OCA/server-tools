# -*- coding: utf-8 -*-
#################################################################################
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
#################################################################################

{
    "name": "Extract Documents from database",
    "summary": "Extract documents from database to the defined filestore",
    "version": "1.0",
    "author": "Julius Network Solutions",
    "website": "http://julius.fr",
    "category": "Tools",
    "depends": [
        "document",
    ],
    "description": """
Button to extract documents from your database
==============================================
If you want to extract the document stored in your database this module is for you.

Make sure you've correctly defined the filestore in your database:
"Settings > Parameters > System Parameters", add for example:
    * "key": "ir_attachment.location"
    * "value": "file:///filestore"

Then go to your document list, select all the documents you want to extract.
Then, "More > Document Extraction"
    """,
    "demo" : [],
    "data" : [
        'document_view.xml'
    ],
    'installable' : True,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: