# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


def pre_init_hook(env):
    """setup vector"""
    env.cr.execute(
        """
        SELECT
            tablename
        FROM
            pg_tables
        WHERE
            tablename='spatial_ref_sys';
    """
    )
    check = env.cr.fetchone()
    if check:
        return {}
    try:
        env.cr.execute(
            """
        CREATE EXTENSION IF NOT EXISTS vector;
    """
        )
    except Exception:
        import logging

        _logger = logging.getLogger(__name__)
        _logger.warning(
            "Could not automatically initialize pgvector support. "
            "Database user may need superuser privileges and pgvector "
            "extension must be installed. To manually prepare your "
            "database, run as superuser:\n"
            "CREATE EXTENSION vector;"
        )
