# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _
from odoo.exceptions import MissingError


def pre_init_hook(cr):
    """setup vector"""
    cr.execute(
        """
        SELECT
            tablename
        FROM
            pg_tables
        WHERE
            tablename='spatial_ref_sys';
    """
    )
    check = cr.fetchone()
    if check:
        return {}
    try:
        cr.execute(
            """
        CREATE EXTENSION IF NOT EXISTS vector;
    """
        )
    except Exception as exc:
        raise MissingError(
            _(
                "Error, can not automatically initialize vector"
                " support. Database user may have to be superuser and"
                " pgvector extensions  to be installed. If you do not"
                " want Odoo to connect with a super user you can manually"
                " prepare your database. To dothis, open a client to your"
                " database using a super user and run:\n"
                "CREATE EXTENSION vector;\n"
            )
        ) from exc
