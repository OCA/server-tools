# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ForbidWriteMixin(models.AbstractModel):
    _name = "forbid.write.mixin"
    _description = "Forbid Write Mixin"

    def _get_forbid_write_fns(self):
        """Return a dict of format
        fn_name: (list[fields], error_message):
        """
        return {}

    def write(self, vals):
        for fn, v in self._get_forbid_write_fns():
            if any(field in vals.keys() for field in v[0]):
                getattr(self, fn)(v[1])
        return super().write(vals)
