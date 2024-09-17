# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "record_changeset_change", "is_informative_change"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE record_changeset_change
            ADD COLUMN is_informative_change boolean
            """,
        )
