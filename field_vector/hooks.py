# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


def pre_init_hook(env):
    """setup vector extension if not already setup"""
    env.cr.execute("SELECT typname, oid FROM pg_type WHERE oid = to_regtype('vector')")
    type_info = dict(env.cr.fetchall())
    if "vector" in type_info:
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
