# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{'name': 'Binary Field',
 'version': '0.0.1',
 'author': 'Akretion',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Framework',
 'description': """This module extend the fields class in order to add 3 new
type of fields.
- BinaryStore
- ImageStore
- ImageRezise

All of this fields will be store on the file system by default and not in the
database. If you want to store it on an other support (database, S3, ftp,
SFTP...)
Then you should create your own 'storage class' and use your custom 'storage
class' instead

The default Storage class will store the field on the file system and build
the path like that

 BASE_LOCATION/DB_NAME/MODEL-FIELD/XXX/YYYYY

with

- BASE_LOCATION: the base location configured in ir.config_parameter
- DB_NAME:  your database name
- MODEL-FIELD: the concatenation of the name of the model with the name of the
field, for example 'product_product-image'
- XXX: the first 3 letter of the file name build with their sha1 hash
- YYYYYY: file name build with their sha1 hash

Here is an example of field declaration

    'binary_test': fields.BinaryField('Test Binary'),
    'image_test': fields.ImageField('Test Image',
        config={
            'field_key': 'StoreMeHere',
            'base_location': 'file:///testpath',
            }),
    'image_test_resize': fields.ImageResizeField(
        related_field='image_test',
        string='Test Image small',
        height=64,
        width=64,
        ),
 """,
 'depends': [
     'web',
 ],
 'data': [
     'data.xml',
     'ir_model_view.xml',
     'storage_view.xml',
 ],
 'js': [
     'static/src/js/widget.js',
 ],
 'installable': True,
 'application': True,
}
