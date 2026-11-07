# Copyright 2025 glueckkanja AG (<https://www.glueckkanja.com>) - Christopher Rogos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from ast import literal_eval
from collections import defaultdict

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.ormcache()
    def _tm_all_tracking_domain_fields(self):
        cr = self.env.cr
        cr.execute(
            """
            SELECT id, model, name, tracking_domain
            FROM ir_model_fields
            WHERE tracking_domain is not null
                and tracking_domain != ''
                and tracking_domain != '[]'
        """
        )
        result = defaultdict(dict)
        for row in cr.dictfetchall():
            result[row["model"]][row["name"]] = row
        return result

    def _tm_post_message(self, data):
        for model_name, model_data in data.items():
            all_tracking_domain_fields = self._tm_all_tracking_domain_fields()[
                model_name
            ]
            # check if any fields with tracking_domain
            if not all_tracking_domain_fields:
                continue
            record_to_remove = []
            for record_id, messages_by_field in model_data.items():
                fields_to_remove = []
                record = self.env[model_name].browse(record_id)
                if not record.exists():
                    # if a record have been modify and then deleted
                    # it's not need to track the change so skip it
                    continue
                for field_name in messages_by_field:
                    field_data = all_tracking_domain_fields.get(field_name, False)
                    if field_data and not record.filtered_domain(
                        literal_eval(field_data["tracking_domain"])
                    ):
                        fields_to_remove.append(field_name)
                for field_name in fields_to_remove:
                    del model_data[record_id][field_name]
                if not messages_by_field:
                    record_to_remove.append(record_id)

            for record_id in record_to_remove:
                del model_data[record_id]
        return super()._tm_post_message(data)


class MailTrackMixin(models.AbstractModel):
    _inherit = "mail.track.mixin"

    def _mail_track(self, tracked_fields, initial_values):
        changes, tracking_value_ids = super()._mail_track(
            tracked_fields, initial_values
        )

        all_tracking_domain_fields = self._tm_all_tracking_domain_fields().get(
            self._name
        )
        if not all_tracking_domain_fields or not tracking_value_ids:
            return changes, tracking_value_ids

        # remove entries that are not matching the tracking_domain of the field
        fields_to_remove_ids = set()
        fields_to_remove_names = set()
        for field_name in tracked_fields:
            field_data = all_tracking_domain_fields.get(field_name, False)
            if field_data and not self.filtered_domain(
                literal_eval(field_data["tracking_domain"])
            ):
                fields_to_remove_ids.add(field_data["id"])
                fields_to_remove_names.add(field_name)

        if not fields_to_remove_ids and not fields_to_remove_names:
            return changes, tracking_value_ids

        res_tracking_value_ids = []
        for tracking_val in tracking_value_ids:
            val_dict = (
                tracking_val[2]
                if isinstance(tracking_val, (list, tuple))
                else tracking_val
            )
            field_id = val_dict.get("field_id")
            field_name = val_dict.get("field_name") or val_dict.get(
                "field_info", {}
            ).get("name")
            if field_id in fields_to_remove_ids or field_name in fields_to_remove_names:
                continue
            res_tracking_value_ids.append(tracking_val)
        tracking_value_ids = res_tracking_value_ids

        if isinstance(changes, set):
            changes = changes - fields_to_remove_names
        elif isinstance(changes, dict):
            changes = {
                k: v
                for k, v in changes.items()
                if k not in fields_to_remove_names and v not in fields_to_remove_names
            }
        else:
            changes = [c for c in changes if c not in fields_to_remove_names]

        return changes, tracking_value_ids
