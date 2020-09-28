# Copyright 2020 Open SOurce Integrators


def pre_init(cr):
    """
    Initialize required pg_trm database extension
    """
    cr.execute(
        """
        SELECT *
        FROM pg_available_extensions
        WHERE installed_version IS NOT NULL
        AND name='pg_trgm';
        """
    )
    pg_trgm_installed = cr.fetchone()
    if not pg_trgm_installed:
        cr.execute(
            """
            CREATE EXTENSION pg_trgm;
            """
        )
