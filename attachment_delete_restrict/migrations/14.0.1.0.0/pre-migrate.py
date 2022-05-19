# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tools.sql import column_exists, rename_column


def migrate(cr, version):
    if column_exists(cr, "ir_model", "restrict_delete_attachment"):
        rename_column(
            cr,
            "ir_model",
            "restrict_delete_attachment",
            "migrated_restrict_delete_attachment",
        )
