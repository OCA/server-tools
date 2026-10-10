# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import date, datetime

from psycopg2 import sql

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


supported_types = ("integer", "many2one", "date", "datetime", "char", "text", "html")


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def validate_ranked_search(self, fields_searches):
        if not fields_searches:
            raise ValidationError(_("No fields provided for search"))
        for field_name, opts in fields_searches.items():
            if "value" not in opts:
                msg = _(f"Value must be provided for field {field_name}")
                raise ValidationError(msg)
            if "coefficient" not in opts:
                raise ValidationError(_("Coefficient must be provided"))
            coef = opts["coefficient"]
            if not isinstance(coef, (int | float)) or not (0 < coef <= 100):
                raise ValidationError(_("Coefficient must be between 0 and 100"))

            if field_name not in self._fields:
                raise ValidationError(_(f"Unknown field {field_name}"))
            field = self._fields[field_name]
            if not field.store:
                raise ValidationError(_(f"Field {field_name} is not stored."))
            ftype = field.type
            if ftype not in supported_types:
                raise ValidationError(_(f"Unsupported field type: {ftype}"))

            # also validate the value based on the field type
            if ftype in ("integer", "many2one"):
                if not isinstance(opts["value"], int):
                    msg = _(f"Value must be an integer for field {field_name}")
                    raise ValidationError(msg)
            elif ftype in ("date", "datetime"):
                if not isinstance(opts["value"], (date | datetime)):
                    msg = _(f"Value must be a date or datetime for field {field_name}")
                    raise ValidationError(msg)
            elif ftype in ("char", "text", "html"):
                # note that in html case, markupsafe.Markup is a string
                if not isinstance(opts["value"], str) or not opts["value"]:
                    msg = _(f"Value must be a nonempty string for field {field_name}")
                    raise ValidationError(msg)

    @api.model
    def ranked_search(self, fields_searches, threshold=0.5, limit=None, domain=None):
        """
        Perform a ranked search on the model using pg_trgm for fuzzy matching.
        :param fields_searches: {
            "field_name": {
                "value": <search_value>,
                "coefficient": <weight 0–100>
            },
            ...
        }
        :param threshold: minimum total score to return
        :param limit: maximum number of records
        :param domain: optional domain to filter records before scoring
        :return: {ID: score} ordered by relevance
        """
        rank_clauses = []
        params = []

        self.validate_ranked_search(fields_searches)

        for field_name, opts in fields_searches.items():
            coef = opts["coefficient"]
            val = opts["value"]
            ftype = self._fields[field_name].type

            if ftype in ("integer", "many2one"):
                # Exact match for numeric fields
                clause = sql.SQL("CASE WHEN {} = %s THEN {} ELSE 0 END").format(
                    sql.Identifier(field_name), sql.Literal(coef)
                )
                params.append(val)

            elif ftype in ("date", "datetime"):
                # Exact match for date fields
                clause = sql.SQL("CASE WHEN {} = %s THEN {} ELSE 0 END").format(
                    sql.Identifier(field_name), sql.Literal(coef)
                )
                params.append(val)

            elif ftype in ("char", "text", "html"):
                clause = sql.SQL(
                    "GREATEST("
                    # 1. Exact case-insensitive match (highest priority)
                    "  CASE WHEN LOWER({}) = LOWER(%s) THEN {} ELSE 0 END,"
                    # 2. pg_trgm similarity scoring (0.0 to 1.0)
                    "  CASE WHEN similarity({}, %s) > 0.1 "
                    "       THEN similarity({}, %s) * {} ELSE 0 END,"
                    # 3. ILIKE substring match (fallback)
                    "  CASE WHEN LOWER({}) LIKE LOWER(%s) THEN {} * 0.3 ELSE 0 END"
                    ")"
                ).format(
                    sql.Identifier(field_name),  # exact match field
                    sql.Literal(coef),  # exact match coefficient
                    sql.Identifier(field_name),  # similarity field 1
                    sql.Identifier(field_name),  # similarity field 2
                    sql.Literal(coef),  # similarity coefficient
                    sql.Identifier(field_name),  # ilike field
                    sql.Literal(coef),  # ilike coefficient
                )
                params.extend(
                    [
                        val,  # exact match value
                        val,  # similarity value 1
                        val,  # similarity value 2
                        f"%{val}%",  # ilike pattern
                    ]
                )
            rank_clauses.append(clause)

        base_query_parts = [
            sql.SQL("SELECT id, ({}) AS score FROM {}").format(
                sql.SQL(" + ").join(rank_clauses), sql.Identifier(self._table)
            )
        ]

        if domain:
            domain_query = self._where_calc(domain)
            where_clause = domain_query.where_clause.code
            where_params = domain_query.where_clause.params
            if where_clause:
                subq = sql.SQL(" WHERE {}").format(sql.SQL(where_clause))
                base_query_parts.append(subq)
                params.extend(where_params)

        query = sql.SQL("""
        WITH ranked AS (
          {}
        )
        SELECT id, score
        FROM ranked
        WHERE score >= %s
        ORDER BY score DESC
        """).format(sql.SQL("").join(base_query_parts))

        params.append(threshold)

        if limit and isinstance(limit, int) and limit > 0:
            query = sql.SQL("{} LIMIT %s").format(query)
            params.append(limit)

        self.env.cr.execute(query, params)
        results = self.env.cr.fetchall()

        return {row[0]: row[1] for row in results}

    def get_scores(self, fields_searches, threshold=0.5, limit=None, domain=None):
        domain = domain or []
        domain_ids = [("id", "in", self.ids)]
        domain = expression.AND([domain, domain_ids])
        return self.ranked_search(fields_searches, threshold, limit, domain)

    def get_score(self, fields_searches, threshold=0.5, limit=None, domain=None):
        self.ensure_one()
        return self.ranked_search(fields_searches, threshold, limit, domain)[self.id]
