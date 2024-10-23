# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Base(models.BaseModel):
    _inherit = "base"

    def copy(self, default=None):
        # OVERRIDE: ``ir.translation._upsert_translations()`` will check for this new
        # context key, to make sure we don't remove translations unless they are
        # actually generated post-copy
        return super(Base, self.with_context(skip_translation_copy=True)).copy(default)

    @api.model
    def _get_field_names_to_skip_in_copy(self) -> list:
        """List of fields to skip when copying translations"""
        return []
