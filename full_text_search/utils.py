# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools.sql import SQL


def to_tsquery(text, lang):
    return SQL(
        "replace(websearch_to_tsquery(%(lang)s::regconfig, "
        "%(text)s)::text || ' ', ''' ', ''':*')::tsquery",
        lang=lang,
        text=text,
    )
