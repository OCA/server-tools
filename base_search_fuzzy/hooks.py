# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 LasLabs Inc.
# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from functools import wraps

from odoo.osv import expression


def patch_leaf_trgm(original):
    @wraps(original)
    def _wrapper(self, leaf, model, alias):
        left, operator, right = leaf
        # No overload for other operators...
        if operator != "%":
            # Except translation "inselect" queries
            if operator == "inselect":
                right = (right[0].replace(" % ", " %% "), right[1])
                leaf = (left, operator, right)
            return original(self, leaf, model, alias)
        # The field must exist
        if left not in model._fields:
            raise ValueError(
                "Invalid field {!r} in domain term {!r}".format(left, leaf)
            )

        # Generate correct WHERE clause part
        query = '("{}"."{}" %% %s)'.format(
            alias,
            left,
        )
        params = [right]
        return query, params

    return _wrapper


def post_load():
    """Patch expression generators to enable the fuzzy search operator."""
    expression.TERM_OPERATORS += ("%",)
    expression.expression._expression__leaf_to_sql = patch_leaf_trgm(
        expression.expression._expression__leaf_to_sql
    )
