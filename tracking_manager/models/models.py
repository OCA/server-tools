# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from collections import defaultdict

from odoo import Command, api, models, tools
from odoo.exceptions import AccessError

from ..tools import format_m2m

# To avoid conflict with other module and avoid too long function name
# specific tracking_manager method are prefixed with _tm


class Base(models.AbstractModel):
    _inherit = "base"

    @tools.ormcache()
    def is_tracked_by_o2m(self):
        return self._name in self.env["ir.model"]._get_model_tracked_by_o2m()

    def _tm_get_fields_to_notify(self):
        return (
            self.env["ir.model"]
            ._get_model_tracked_by_o2m()
            .get(self._name, {})
            .get("notify", [])
        )

    def _tm_get_fields_to_track(self):
        # We track manually
        # all fields that belong to a model tracked via a one2many
        # all the many2many fields
        return (
            self.env["ir.model"]
            ._get_model_tracked_by_o2m()
            .get(self._name, {})
            .get("fields", [])
        )

    def _tm_notify_owner(self, mode, changes=None):
        """Notify all model that have a one2many linked to the record changed"""
        self.ensure_one()
        data = self.env.cr.precommit.data.setdefault(
            "tracking.manager.data",
            defaultdict(lambda: defaultdict(lambda: defaultdict(list))),
        )
        for field_name, owner_field_name in self._tm_get_fields_to_notify():
            owner = self[field_name]
            # Skip processing if the owner is not a valid Odoo recordset or is empty.
            if not (owner and isinstance(owner, models.BaseModel)):
                continue
            data[owner._name][owner.id][owner_field_name].append(
                {
                    "mode": mode,
                    "record": self.display_name,
                    "changes": changes,
                }
            )

    def _tm_get_field_description(self, field_name):
        return self._fields[field_name].get_description(self.env)["string"]

    def _tm_get_changes(self, values):
        self.ensure_one()
        changes = []
        for field_name, before in values.items():
            field = self._fields[field_name]
            if before != self[field_name]:
                if field.type == "many2many":
                    old = format_m2m(before)
                    new = format_m2m(self[field_name])
                elif field.type == "many2one":
                    old = before.display_name
                    new = self[field_name]["display_name"]
                else:
                    old = before
                    new = self[field_name]
                changes.append(
                    {
                        "name": self._tm_get_field_description(field_name),
                        "old": old,
                        "new": new,
                    }
                )
        return changes

    def _tm_post_message(self, data):
        for model_name, model_data in data.items():
            # check if record has mail.thread mixin
            if not getattr(self.env[model_name], "message_post_with_source", False):
                continue
            for record_id, messages_by_field in model_data.items():
                # Avoid error if no record is linked (example: child_ids of res.partner)
                if not record_id:
                    continue
                record = self.env[model_name].browse(record_id)
                messages = [
                    {
                        "name": record._tm_get_field_description(field_name),
                        "messages": messages,
                    }
                    for field_name, messages in messages_by_field.items()
                ]
                # We do not use message_post_with_view() because emails would be sent
                rendered_template = self.env["ir.qweb"]._render(
                    "tracking_manager.track_o2m_m2m_template",
                    {"lines": messages, "object": record},
                    minimal_qcontext=True,
                )
                record._message_log(body=rendered_template)

    def _tm_prepare_o2m_tracking(self):
        fnames = self._tm_get_fields_to_track()
        if not fnames:
            return
        self.env.cr.precommit.add(self._tm_finalize_o2m_tracking)
        initial_values = self.env.cr.precommit.data.setdefault(
            f"tracking.manager.before.{self._name}", {}
        )
        for record in self:
            values = initial_values.setdefault(record.id, {})
            if values is not None:
                for fname in fnames:
                    try:
                        values.setdefault(fname, record[fname])
                    except AccessError:
                        # User does not have access to the field (example with groups)
                        continue

    def _tm_finalize_o2m_tracking(self):
        initial_values = self.env.cr.precommit.data.pop(
            f"tracking.manager.before.{self._name}", {}
        )
        for _id, values in initial_values.items():
            # Always use sudo in case that the record have been modified using sudo
            record = self.sudo().browse(_id)
            if not record.exists():
                # if a record have been modify and then deleted
                # it's not need to track the change so skip it
                continue
            changes = record._tm_get_changes(values)
            if changes:
                record._tm_notify_owner("update", changes)
        data = self.env.cr.precommit.data.pop("tracking.manager.data", {})
        self._tm_post_message(data)
        self.flush_model()

    def _tm_track_create_unlink(self, mode):
        self.env.cr.precommit.add(self._tm_finalize_o2m_tracking)
        for record in self:
            record._tm_notify_owner(mode)

    def write(self, vals):
        if self.is_tracked_by_o2m():
            self._tm_prepare_o2m_tracking()
        return super().write(vals)

    @api.model_create_multi
    def create(self, list_vals):
        records = super().create(list_vals)
        if self.is_tracked_by_o2m():
            records._tm_track_create_unlink("create")
        return records

    def unlink(self):
        if self.is_tracked_by_o2m():
            self._tm_track_create_unlink("unlink")
        return super().unlink()

    # TODO: Remove if merged https://github.com/odoo/odoo/pull/156236
    def _mail_track(self, tracked_fields, initial_values):
        _tracked_fields = tracked_fields
        tracked_fields_properties = {}
        for tf_key in list(_tracked_fields.keys()):
            tracked_field = tracked_fields[tf_key]
            if tracked_field["type"] == "properties":
                tracked_fields_properties[tf_key] = tracked_field
        updated, tracking_value_ids = super()._mail_track(
            tracked_fields, initial_values
        )
        # Remove unnecessary tracking_value_ids
        tracking_value_ids_keys_to_delete = []
        for tf_key in list(tracked_fields_properties.keys()):
            field = self.env["ir.model.fields"]._get(self._name, tf_key)
            for key, vals in enumerate(tracking_value_ids):
                if vals[2]["field_id"] == field.id:
                    tracking_value_ids_keys_to_delete.append(key)
        for key in tracking_value_ids_keys_to_delete:
            tracking_value_ids.pop(key)
        # Extra things for properties
        for col_name, _sequence in self._mail_track_order_fields(
            tracked_fields_properties
        ):
            if col_name not in initial_values:
                continue
            initial_value, new_value = initial_values[col_name], self[col_name]
            if new_value == initial_value or (not new_value and not initial_value):
                continue
            p_keys = list(initial_value.keys()) if initial_value else []
            properties_data = {}
            for definition in self.read([col_name])[0][col_name]:
                properties_data[definition["name"]] = definition
            tracking_value_ids.extend(
                Command.create(
                    self.env["mail.tracking.value"]._create_tracking_values_property(
                        initial_value[p_key],
                        new_value[p_key],
                        col_name,
                        properties_data[p_key],
                        self,
                    ),
                )
                for p_key in p_keys
                if (
                    p_key in properties_data
                    and properties_data[p_key]["type"] != "separator"
                    and initial_value[p_key] != new_value[p_key]
                )
            )
        return updated, tracking_value_ids
