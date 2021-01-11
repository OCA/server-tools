# Copyright 2021 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, fields, models
from odoo.exceptions import AccessError


class RestrictEditionMixin(models.AbstractModel):
    _name = "restrict.edition.mixin"

    restrict_edition_to_superuser = fields.Boolean()

    def check_access_rule(self, operation):
        if operation in ("write", "unlink"):
            for rec in self:
                if (
                    rec.restrict_edition_to_superuser
                    and not self.env.user.id == SUPERUSER_ID
                ):
                    raise AccessError(_("Only the administrator can edit this record"))
        super().check_access_rule(operation)
