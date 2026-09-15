# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools.sql import SQL

from ..utils import to_tsquery


class Base(models.AbstractModel):
    _inherit = "base"

    def _condition_to_sql(self, alias, fname, operator, value, query):
        if operator == "@@":
            field = self._fields[fname]
            value = to_tsquery(value, field.dictionary)

        return super()._condition_to_sql(alias, fname, operator, value, query)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        query = super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
        )

        if (not order or order == self._order) and query.order:
            # If no order is specified and a full text search argument is found
            # order by the full text search rank
            for leaf in domain:
                if isinstance(leaf, tuple | list) and leaf[1] == "@@":
                    field_name, _, value = leaf
                    field = self._fields.get(field_name)
                    if field:
                        if field.inherited:
                            field = field.base_field
                        if field.store and field.column_type:
                            alias = self._table
                            sql_field = self._field_to_sql(alias, field_name, query)
                            query.order = SQL(", ").join(
                                [
                                    SQL(
                                        "ts_rank_cd(%(sql_field)s, %(tsquery)s) desc",
                                        sql_field=sql_field,
                                        tsquery=to_tsquery(value, field.dictionary),
                                    ),
                                    query.order,
                                ]
                            )
        return query
