# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists


@openupgrade.migrate()
def migrate(env, version):
    if column_exists(env.cr, "ir_model", "migrated_restrict_delete_attachment"):
        query = """
        SELECT id FROM ir_model WHERE migrated_restrict_delete_attachment = True
        """
        env.cr.execute(query)
        results = env.cr.fetchall()
        models = env["ir.model"].search([("id", "in", results)])
        for model in models:
            model.restrict_delete_attachment = "custom"

        query2 = "ALTER TABLE ir_model DROP COLUMN migrated_restrict_delete_attachment;"
        env.cr.execute(query2)
