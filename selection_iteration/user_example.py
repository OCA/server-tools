# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
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

from openerp.osv import orm, fields


class UsersExample(orm.Model):
    _inherit = ['res.users', 'abstract.selection.rotate']
    _name = 'res.users'

    def _get_selection_values(self, cr, uid, context=None):
        # with the method above you can inherit this method
        return [
            ('val1', 'Val1'),
            ('val2', 'Val2'),
            ('val3', 'Val3'),
            ]

    def __get_selection_values(self, cr, uid, context=None):
        # intermediate method for inherit
        # if not present you cannot inherit selection method
        return self._get_selection_values(cr, uid, context=context)

    _columns = {
        "select_iter": fields.selection(
            __get_selection_values,
            string="Selection iterable",
            readonly=True
            )
        }

    def _get_values_from_selection(self, cr, uid, ids, field, context=None):
        res = super(UsersExample, self)._get_values_from_selection(
            cr, uid, ids, field, context=context
            )
        if field == 'select_iter':
            # also check model name ?
            res = self._get_selection_values(cr, uid, context=context)
        return res
