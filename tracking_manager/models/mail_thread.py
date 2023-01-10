# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, tools


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_custom_tracked_fields(self):
        fields_per_models = self.env["ir.model"]._get_custom_tracked_fields_per_model()
        if self._name in fields_per_models:
            return fields_per_models[self._name]
        else:
            return None

    @tools.ormcache("self.env.uid", "self.env.su")
    def _get_tracked_fields(self):
        res = super()._get_tracked_fields()
        custom_tracked_fields = self._get_custom_tracked_fields()
        if custom_tracked_fields is not None:
            return set(custom_tracked_fields)
        return res

    def _track_m2m_change(self, vals):
        custom_tracked_fields = self._get_custom_tracked_fields()
        if custom_tracked_fields:
            for record in self:
                for field_name in custom_tracked_fields:
                    if (
                        field_name in vals
                        and self._fields[field_name].type == "many2many"
                    ):
                        removed, added = record._tm_get_m2m_change(
                            field_name, vals[field_name]
                        )
                        if removed:
                            for record_name in removed:
                                record._tm_add_message(
                                    "unlink", record_name, field_name
                                )
                        if added:
                            for record_name in added:
                                record._tm_add_message(
                                    "create", record_name, field_name
                                )

    def _tm_track_write(self, vals):
        super()._tm_track_write(vals)
        self._track_m2m_change(vals)
