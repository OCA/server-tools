# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.osv import expression
from odoo.tools.sql import SQL


def post_load():
    # Add full text search operator
    expression.TERM_OPERATORS += ("@@",)
    expression.SQL_OPERATORS.update({"@@": SQL("@@")})
