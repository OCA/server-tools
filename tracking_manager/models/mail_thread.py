# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, tools


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @tools.ormcache("self.env.uid", "self.env.su")
    def _track_get_fields(self):
        fields_per_models = self.env["ir.model"]._get_custom_tracked_fields_per_model()
        if self._name in fields_per_models:
            # One2many fields are tracked by tracking_manager itself (see
            # _tm_notify_owner), exclude them from the standard tracking to
            # avoid logging the full list of related records
            fnames = [
                fname
                for fname in fields_per_models[self._name]
                if self._fields[fname].type != "one2many"
            ]
            return set(self.fields_get(fnames)) if fnames else set()
        else:
            return super()._track_get_fields()
