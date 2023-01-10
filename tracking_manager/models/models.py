# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from collections import defaultdict, namedtuple

from odoo import _, api, models

# To avoid conflict with other module and avoid too long function name
# all tracking_manager method are prefixed with _tm


Tracker = namedtuple("TmTracker", ["model", "data"])


class Base(models.AbstractModel):
    _inherit = "base"

    @property
    def _tm_o2m_field_to_notify(self):
        if self._name in ["ir.model", "ir.model.fields"]:
            return []
        return (
            self.env["ir.model"]
            ._get_o2m_trackable_model()
            .get(self._name, {})
            .get("notify", [])
        )

    @property
    def _tm_o2m_field_to_track(self):
        if self._name in ["ir.model", "ir.model.fields"]:
            return []
        return (
            self.env["ir.model"]
            ._get_o2m_trackable_model()
            .get(self._name, {})
            .get("fields", [])
        )

    def _tm_init_tracker(self):
        if self._context.get("tm_tracker") and not hasattr(self, "_mail_flat_thread"):
            # The current model do not support message_ids (the class is not inherited
            # from mail thread) and the change is done from a model that support
            # the message_ids, so message should be posted there
            return self
        else:
            tm_tracker = Tracker(self._name, defaultdict(lambda: defaultdict(list)))
            return self.with_context(tm_tracker=tm_tracker)

    def _tm_add_message(self, mode, record_name, field_name, changes=None):
        self.ensure_one()
        tracker = self._context.get("tm_tracker")
        tracker.data[self][field_name].append(
            {
                "mode": mode,
                "record": record_name,
                "changes": changes,
            }
        )

    def _tm_notify_owner(self, mode, changes=None):
        """Notify all model that have a one2many linked to the record changed"""
        self.ensure_one()
        for field_name, inverse_field_name in self._tm_o2m_field_to_notify:
            self[field_name]._tm_add_message(
                mode, self.display_name, inverse_field_name, changes
            )

    def _tm_get_m2m_change(self, field_name, value):
        self.ensure_one()
        if len(value) == 1 and len(value[0]) == 3 and value[0][0] == 6:
            new_ids = set(value[0][2])
            old_ids = set(self[field_name].ids)
            if new_ids != old_ids:
                removed_ids = old_ids - new_ids
                added_ids = new_ids - old_ids
                return (
                    self[field_name].browse(removed_ids).mapped("display_name"),
                    self[field_name].browse(added_ids).mapped("display_name"),
                )
        return [], []

    def _tm_get_changes(self, fields, vals):
        # TODO track change correctly (m2m, m2o...)
        self.ensure_one()
        changes = []
        for field in fields:
            if self[field] != vals[field]:
                changes.append(
                    {
                        "name": _(self._fields[field].string),
                        "old": self[field],
                        "new": vals[field],
                    }
                )
        return changes

    def _tm_track_write(self, vals):
        tracked_fields = set(self._tm_o2m_field_to_track) & (vals.keys())
        if tracked_fields:
            for record in self:
                changes = record._tm_get_changes(tracked_fields, vals)
                record._tm_notify_owner("update", changes)

    def _tm_post_message(self):
        tracker = self._context.get("tm_tracker")
        if tracker and tracker.model == self._name and tracker.data:
            for record, messages_by_field in tracker.data.items():
                messages = [
                    {
                        "messages": messages,
                        "name": _(record._fields[field_name].string),
                    }
                    for field_name, messages in messages_by_field.items()
                ]
                record.message_post_with_view(
                    "tracking_manager.track_o2m_m2m_template",
                    values={"lines": messages},
                    subtype_id=self.env.ref("mail.mt_note").id,
                )

    def write(self, vals):
        self = self._tm_init_tracker()
        self._tm_track_write(vals)
        res = super().write(vals)
        self._tm_post_message()
        return res

    @api.model_create_multi
    def create(self, list_vals):
        self = self._tm_init_tracker()
        records = super().create(list_vals)
        records._tm_notify_owner("create")
        self._tm_post_message()
        return records

    def unlink(self):
        self = self._tm_init_tracker()
        for record in self:
            record._tm_notify_owner("unlink")
        res = super().unlink()
        self._tm_post_message()
        return res
