# -*- encoding: utf-8 -*-
##############################################################################
#
#    Module - Parent Dependencies module for Odoo
#    Copyright (C) 2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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
    'name': 'Parent Dependencies of Modules',
    'version': '0.1',
    'summary': """allows to see the list of modules dependencies of a given"""
    """ module, at the full depth of the dependency tree""",
    'category': 'Tools',
    'description': """
allows to see the list of modules dependencies of a given module, at the"""
    """ full depth of the dependency tree
========================================================================"""
    """==================================

Functionality:
--------------
    * This module allows to see the list of modules dependencies of a"""
    """ given module, at the full depth of the dependency tree.

Copyright, Authors and Licence:
-------------------------------
    * Copyright: 2014, GRAP: Groupement Régional Alimentaire de Proximité;
    * Author: Sylvain LE GAL (https://twitter.com/legalsylvain);""",
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'view/view.xml',
    ],
    'images': [
        'static/src/img/screenshots/dependencies_list.jpg'
    ],
}
