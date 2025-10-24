# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    # Workaround to execute the migration script without errors
    # see https://github.com/odoo/odoo/blob/2a839ef1ed09c36f27ce7536ca3052d9f65ceed9/odoo/modules/migration.py#L252-L256
    env = cr
    env.cr.execute(
        """
        SELECT imf.model
        FROM ir_model_fields AS imf
        WHERE imf.name = 'review_ids'
        AND imf.ttype = 'one2many'
        AND imf.model != 'tier.validation'
        """
    )
    for (model_name,) in env.cr.fetchall():
        table_name = model_name.replace(".", "_")
        # validation_status column
        if not openupgrade.column_exists(env.cr, table_name, "validation_status"):
            openupgrade.logged_query(
                env.cr,
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN IF NOT EXISTS validation_status VARCHAR
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'no'
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'rejected'
                WHERE validation_status = 'no' AND id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}' AND tr.status = 'rejected'
                )
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'pending'
                WHERE validation_status = 'no' AND id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}' AND tr.status = 'pending'
                )
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'waiting'
                WHERE validation_status = 'no' AND id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}' AND tr.status = 'waiting'
                )
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'validated'
                WHERE validation_status = 'no' AND id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}'
                    AND tr.status IN ('approved', 'forwarded')
                )
                """,
            )
