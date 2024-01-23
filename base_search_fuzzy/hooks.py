# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 LasLabs Inc.
# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.osv import expression
from odoo.tools.sql import SQL


def post_load():
    """Patch expression generators to enable the fuzzy search operator."""
    expression.TERM_OPERATORS += ("%",)
    expression.SQL_OPERATORS.update({"%": SQL("%%")})
