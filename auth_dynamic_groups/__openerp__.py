# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
    "name": "Dynamic groups",
    "version": "1.0",
    "author": "Therp BV",
    "complexity": "normal",
    "description": """
Description
-----------
This module allows defining groups whose membership is a condition expressed as
python code. For every user, it is evaluated during login if she belongs to
the group or not.

Usage
-----
Check `Dynamic` on a group you want to be dynamic. Now fill in the condition,
using `user` which is a browse record of the user in question that evaluates
truthy if the user is supposed to be a member of the group and falsy if not.

There is a constraint on the field to check for validity if this expression.
When you're satisfied, click the button `Evaluate` to prefill the group's
members. The condition will be checked now for every user who logs in.
    """,
    "category": "Tools",
    "depends": [
        'base',
    ],
    "data": [
        'view/res_groups.xml',
    ],
    "auto_install": False,
    "installable": True,
    "external_dependencies": {
        'python': [],
    },
}
