# Copyright 2016 ForgeFlow S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


def patch_leaf_trgm(method):
    def decorate_leaf_to_sql(self, eleaf):
        model = eleaf.model
        leaf = eleaf.leaf
        left, operator, right = leaf
        table_alias = '"%s"' % (eleaf.generate_alias())

        if operator == "%":

            sql_operator = "%%"
            params = []

            if left in model._fields:
                column = "{}.{}".format(table_alias, expression._quote(left))
                query = "({} {} {})".format(
                    column, sql_operator, model._fields[left].column_format,
                )
            elif left in models.MAGIC_COLUMNS:
                query = '({}."{}" {} %s)'.format(table_alias, left, sql_operator)
                params = right
            else:  # Must not happen
                raise ValueError(
                    _("Invalid field {!r} in domain term {!r}".format(left, leaf))
                )

            if left in model._fields:
                params = str(right)

            if isinstance(params, str):
                params = [params]
            return query, params
        elif operator == "inselect":
            right = (right[0].replace(" % ", " %% "), right[1])
            eleaf.leaf = (left, operator, right)
        return method(self, eleaf)

    decorate_leaf_to_sql.__decorated__ = True

    return decorate_leaf_to_sql


def patch_generate_order_by(method):
    @api.model
    def decorate_generate_order_by(self, order_spec, query):
        if order_spec and order_spec.startswith("similarity("):
            return " ORDER BY " + order_spec
        return method(self, order_spec, query)

    decorate_generate_order_by.__decorated__ = True

    return decorate_generate_order_by


class IrModel(models.Model):

    _inherit = "ir.model"

    def _register_hook(self):
        # We have to prevent wrapping the function twice to avoid recursion
        # errors
        if not hasattr(expression.expression._expression__leaf_to_sql, "__decorated__"):
            expression.expression._expression__leaf_to_sql = patch_leaf_trgm(
                expression.expression._expression__leaf_to_sql
            )

        if "%" not in expression.TERM_OPERATORS:
            expression.TERM_OPERATORS += ("%",)

        if not hasattr(models.BaseModel._generate_order_by, "__decorated__"):
            models.BaseModel._generate_order_by = patch_generate_order_by(
                models.BaseModel._generate_order_by
            )
        return super()._register_hook()
