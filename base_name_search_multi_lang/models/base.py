# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models, tools
from odoo.osv import expression
from odoo.tools import SQL

# Other operators compare the value as a whole, where matching another
# language makes no sense
PATTERN_OPERATORS = ("like", "ilike", "not like", "not ilike", "=like", "=ilike")


class Base(models.AbstractModel):
    _inherit = "base"

    @tools.ormcache("self._name")
    def _name_search_multi_lang_enabled(self):
        """Whether this model is searched in all the installed languages"""
        data = (
            self.env["ir.model"]
            .sudo()
            .search_read([("model", "=", self._name)], ["name_search_multi_lang"])
        )
        return bool(data and data[0]["name_search_multi_lang"])

    def _condition_to_sql(self, alias, fname, operator, value, query):
        """Match a translated field in every language

        The standard implementation only matches the current language, with a
        fallback on the company ones.
        """
        sql = super()._condition_to_sql(alias, fname, operator, value, query)
        field = self._fields.get(fname)
        if (
            field is None
            or not field.translate
            or not field.store
            or operator not in PATTERN_OPERATORS
            or not isinstance(value, str)
            or not value
            or not self._name_search_multi_lang_enabled()
        ):
            return sql
        # All languages live in the same jsonb column, and this is the
        # expression a trigram index is built on, so such an index is still used
        sql_langs = self.env.registry.unaccent(
            SQL(
                "jsonb_path_query_array(%s, '$.*')::text",
                SQL.identifier(alias, fname, to_flush=field),
            )
        )
        sql_like = SQL("ILIKE") if operator.endswith("ilike") else SQL("LIKE")
        sql_pattern = self.env.registry.unaccent(
            SQL("%s", value if operator.startswith("=") else f"%{value}%")
        )
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            # Exclude the record as soon as one language matches
            return SQL(
                "(%s AND (%s IS NULL OR %s NOT %s %s))",
                sql,
                sql_langs,
                sql_langs,
                sql_like,
                sql_pattern,
            )
        return SQL("(%s OR %s %s %s)", sql, sql_langs, sql_like, sql_pattern)
