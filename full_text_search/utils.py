# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs, QuotedString

from odoo.tools import pycompat


def to_tsquery(text, lang):
    text = QuotedString(text)
    text.encoding = "utf-8"
    text = pycompat.to_text(text.getquoted())
    return AsIs(
        "replace("
        f"websearch_to_tsquery({lang!r}::regconfig, "  # noqa:E231
        f"{text})::text "  # noqa:E231
        "|| ' ', ''' ', ''':*'"
        ")::tsquery"
    )
