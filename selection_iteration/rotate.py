# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2015 Akretion
#    @author David BEAL <david.beal@akretion.com>
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
###############################################################################

from openerp.osv import orm


def get_neighbor_element(my_itr, initial=None):
    try:
        val = my_itr.next()
        if initial:
            while val != initial:
                val = my_itr.next()
            val = my_itr.next()
        return val
    except StopIteration:
        return None


class AbstractSelectionRotate(orm.Model):
    _name = 'abstract.selection.rotate'

    def _iter_selection(self, cr, uid, ids, direction, context=None):
        " Allows to update the field selection value "
        if 'selection_field' not in context:
            return True
        field = context['selection_field']
        # extract first value in each tuple as content of the selection field
        values = [elm[0]
                  for elm in self._get_values_from_selection(
                      cr, uid, ids, field, context=context)]
        if direction == 'prev':
            values = reversed(values)
        my_itr = iter(values)
        for item in self.browse(cr, uid, ids, context=context):
            initial = item[field]
            value = get_neighbor_element(my_itr, initial)
            if value is None:
                my_itr = iter(values)
                value = get_neighbor_element(my_itr)
            self.write(cr, uid, item.id, {field: value},
                       context=context)
        return True

    def iter_selection_next(self, cr, uid, ids, context=None):
        """ You can trigger this method by this xml declaration
            in your own view to iterate field selection

            <button name="iter_selection_next"
                    context="{'selection_field': 'my_selection_field'}"
                    icon="gtk-go-forward"
                    type="object"/>
        """
        self._iter_selection(cr, uid, ids, 'next', context=context)
        return True

    def iter_selection_prev(self, cr, uid, ids, context=None):
        " see previous method "
        self._iter_selection(cr, uid, ids, 'prev', context=context)
        return True

    def _get_values_from_selection(self, cr, uid, ids, field, context=None):
        """ Override this method
            to return your own list of tuples
            which match with field selection values or a sub part

            [('val1', 'My Val1'),
             ('val2', 'My Val2')]
        """
        return [(), ]
