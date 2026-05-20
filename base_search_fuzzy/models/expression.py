# Copyright 2016 ForgeFlow S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Domain
from odoo.orm.domains import operator_optimization
from odoo.tools import SQL


@operator_optimization(["%"])
def _optimize_trigram_similarity(condition, model):
    """Register the PostgreSQL pg_trgm similarity operator ``%``.

    Emits ``(<field>) %% <value>``; the parentheses keep the predicate
    valid for translatable fields (jsonb accessors).
    """
    field_expr = condition.field_expr
    value = condition.value

    def _to_sql(model_, alias, query):
        sql_field = model_._field_to_sql(alias, field_expr, query)
        return SQL("(%s) %% %s", sql_field, value)

    return Domain.custom(to_sql=_to_sql)
