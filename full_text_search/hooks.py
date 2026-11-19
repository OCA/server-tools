# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from functools import wraps

from odoo.osv import expression

from .utils import to_tsquery


def patch_leaf_to_sql(original):
    @wraps(original)
    def _wrapper(self, leaf, model, alias):
        left, operator, right = leaf
        query, params = original(self, leaf, model, alias)

        if operator == "@@" and params:
            field = model._fields[left]
            params[0] = to_tsquery(params[0], field.dictionary)
        return query, params

    return _wrapper


def post_load():
    # Add full text search operator
    expression.TERM_OPERATORS += ("@@",)
    expression.expression._expression__leaf_to_sql = patch_leaf_to_sql(
        expression.expression._expression__leaf_to_sql
    )
