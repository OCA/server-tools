# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import models
from openerp.osv import expression


_logger = logging.getLogger(__name__)


def patch_leaf_trgm(method):
    def decorate_leaf_to_sql(self, eleaf):
        model = eleaf.model
        leaf = eleaf.leaf
        left, operator, right = leaf
        table_alias = '"%s"' % (eleaf.generate_alias())

        if operator == '%':
            sql_operator = '%%'
            params = []

            if left in model._columns:
                format = model._columns[left]._symbol_set[0]
                column = '%s.%s' % (table_alias, expression._quote(left))
                query = '(%s %s %s)' % (column, sql_operator, format)
            elif left in expression.MAGIC_COLUMNS:
                query = "(%s.\"%s\" %s %%s)" % (
                    table_alias, left, sql_operator)
                params = right
            else:  # Must not happen
                raise ValueError(
                    "Invalid field %r in domain term %r" % (left, leaf))

            if left in model._columns:
                params = model._columns[left]._symbol_set[1](right)

            if isinstance(params, basestring):
                params = [params]
            return query, params
        elif operator == 'inselect':
            right = (right[0].replace(' % ', ' %% '), right[1])
            eleaf.leaf = (left, operator, right)
        return method(self, eleaf)

    return decorate_leaf_to_sql


def patch_generate_order_by(method):
    def decorate_generate_order_by(self, order_spec, query):
        if order_spec and order_spec.startswith('similarity('):
            return ' ORDER BY ' + order_spec
        return method(self, order_spec, query)

    return decorate_generate_order_by


class IrModel(models.Model):

    _inherit = 'ir.model'

    def _register_hook(self, cr, ids=None):
        expression.expression._expression__leaf_to_sql = patch_leaf_trgm(
            expression.expression._expression__leaf_to_sql)

        expression.TERM_OPERATORS += ('%',)

        models.BaseModel._generate_order_by = patch_generate_order_by(
            models.BaseModel._generate_order_by)

        return super(IrModel, self)._register_hook(cr)
