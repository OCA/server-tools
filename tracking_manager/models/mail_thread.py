# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, tools


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @tools.ormcache("self.env.uid", "self.env.su")
    def _get_tracked_fields(self):
        res = super()._get_tracked_fields()
        custom_tracked_fields = self._get_custom_tracked_fields()
        if custom_tracked_fields:
            return custom_tracked_fields
        return res

    def _get_custom_tracked_fields(self):
        tracking_model = (
            self.env["ir.model"]
            .sudo()
            .search(
                [("model", "=", self._name), ("apply_custom_tracking", "=", True)],
                limit=1,
            )
        )
        if tracking_model:
            track_fields = tracking_model.custom_tracking_field_ids.filtered(
                lambda f: f.custom_tracking
            ).mapped("name")
            return track_fields and set(self.fields_get(track_fields))
        return

    def _create_tracking_message(self, mode, field_id, record):
        return {
            "mode": mode,
            "name": field_id.field_description,
            "record": self._get_tracked_record_name(record),
        }

    def _get_tracked_record_name(self, record):
        return (
            getattr(record, "display_name", False)
            or getattr(record, "name", False)
            or f"No name, record :{record}"
        )

    def write(self, vals):
        fields = list(vals.keys())
        tracked_fields = self._get_custom_tracked_fields()
        m2m_o2m_tracked_message = []
        records = []
        if tracked_fields:
            records = [f for f in fields if f in tracked_fields]
            for field in records:
                del_and_chg_records = self._get_m2m_m2o_tracked_fields(
                    field, tracked_fields, vals
                )
                if del_and_chg_records:
                    m2m_o2m_tracked_message.extend(del_and_chg_records)
        res = super().write(vals)
        for field in records:
            add_records = self._check_o2m_add_lines(field, tracked_fields, vals)
            if add_records:
                m2m_o2m_tracked_message.extend(add_records)
        if m2m_o2m_tracked_message:
            self._post_custom_tracking_message(m2m_o2m_tracked_message)
        return res

    def _get_m2m_m2o_tracked_fields(self, field, tracked_fields, vals):
        field_id = self.env["ir.model.fields"].search(
            [("name", "=", field), ("model_id", "=", self._name)], limit=1
        )
        message = []
        if field in tracked_fields and field_id.ttype in ["one2many", "many2many"]:
            if field_id.ttype == "one2many":
                message.extend(self._check_o2m_delete_lines(field_id, vals))
                message.extend(self._check_o2m_change_in_lines(field_id, vals))
            if field_id.ttype == "many2many":
                message.extend(self._check_m2m_tracking(field_id, vals))
        return message

    def _check_o2m_delete_lines(self, field_id, vals):
        lines = [line for line in vals[field_id.name]]
        del_message = []
        for line in lines:
            if line[0] in [2, 3]:
                record = getattr(self, field_id.name).browse(line[-1] or line[1])
                message_line = self._create_tracking_message("Delete", field_id, record)
                del_message.append(message_line)
        return del_message

    def _check_o2m_change_in_lines(self, field_id, vals):
        lines = [line for line in vals[field_id.name] if line[0] in [0, 1]]
        chg_message = []
        for line in lines:
            if len(line) == 3 and line[0] == 1:
                record = getattr(self, field_id.name).browse(line[1])
                line_fields = [f for f in line[2]]
                message_line = self._create_tracking_message("Change", field_id, record)
                changes = []
                for line_field in line_fields:
                    line_field_id = self.env["ir.model.fields"].search(
                        [("name", "=", line_field), ("model", "=", record._name)],
                        limit=1,
                    )
                    line_model_id = self.env["ir.model"].search(
                        [("model", "=", record._name)], limit=1
                    )
                    # if the o2m related model is configured for custom
                    # tracking (apply_custom_tracking = True), we track
                    # the changes only for fields with custom_tracking.
                    if (
                        line_model_id.apply_custom_tracking
                        and not line_field_id.custom_tracking_id.custom_tracking
                    ):
                        old = new = False
                    elif line_field_id.ttype in ["one2many", "many2one", "many2many"]:
                        old_ids = getattr(record, line_field).ids
                        if line[2][line_field]:
                            new_ids = line[2][line_field][0][2]
                            new_line_ids = set(new_ids) - set(old_ids)
                            delete_line_ids = set(old_ids) - set(new_ids)
                            old = ", ".join(
                                getattr(record, line_field)
                                .browse(delete_line_ids)
                                .mapped("name")
                            )
                            new = ", ".join(
                                getattr(record, line_field)
                                .browse(new_line_ids)
                                .mapped("name")
                            )
                    else:
                        old = getattr(record, line_field)
                        new = line[2][line_field]
                    if old != new:
                        changes.append(
                            {
                                "name": line_field,
                                "old": old,
                                "new": new,
                            }
                        )
                if changes:
                    message_line["changes"] = changes
                    chg_message.append(message_line)
        return chg_message

    def _check_o2m_add_lines(self, field, tracked_fields, vals):
        field_id = self.env["ir.model.fields"].search(
            [("name", "=", field), ("model_id", "=", self._name)], limit=1
        )
        if field in tracked_fields and vals.get(field) and field_id.ttype == "one2many":
            message = []
            line_ids_in_vals = [
                line[1]
                for line in vals[field]
                if line[0] != 4 or (line[0] == 4 and not line[-1])
            ]
            new_ids = [
                line
                for line in [line.id for line in getattr(self, field)]
                if line not in line_ids_in_vals
            ]
            for line in new_ids:
                record = getattr(self, field).browse(line)
                message_line = self._create_tracking_message("New", field_id, record)
                message.append(message_line)
            return message

    def _check_m2m_tracking(self, field_id, vals):
        m2m_message = []
        new_ids = [line[-1] for line in vals[field_id.name] if line[0] in [0, 4]]
        delete_ids = [line[-1] for line in vals[field_id.name] if line[0] in [2, 3]]
        new_line_ids = set(new_ids) - set(getattr(self, field_id.name).ids)
        for line in new_line_ids:
            record = getattr(self, field_id.name).browse(line)
            message_line = self._create_tracking_message("New", field_id, record)
            m2m_message.append(message_line)
        for line in delete_ids:
            record = getattr(self, field_id.name).browse(line)
            message_line = self._create_tracking_message("Delete", field_id, record)
            m2m_message.append(message_line)
        return m2m_message

    def _post_custom_tracking_message(self, message):
        formated_message = []
        for field in {line["name"] for line in message}:
            message_by_field = {"name": field, "message_by_field": []}
            modes = {line["mode"] for line in message if line["name"] == field}
            for mode in modes:
                message_by_mode = {"mode": mode}
                for line in message:
                    if line["name"] == field and line["mode"] == mode:
                        message_by_mode["record"] = line["record"]
                        if line.get("changes", False):
                            message_by_mode["changes"] = line["changes"]
                        message_by_field["message_by_field"].append(message_by_mode)
            formated_message.append(message_by_field)
            self.message_post_with_view(
                "tracking_manager.track_o2m_m2m_template",
                values={
                    "lines": formated_message,
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )
