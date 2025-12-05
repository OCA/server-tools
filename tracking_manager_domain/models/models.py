# Copyright 2025 glueckkanja AG (<https://www.glueckkanja.com>) - Christopher Rogos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from ast import literal_eval
from collections import defaultdict

from odoo import models, tools


class Base(models.AbstractModel):
    _inherit = "base"

    @tools.ormcache()
    def _tm_all_tracking_domain_fields(self):
        cr = self._cr
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
                for field_name, _messages in messages_by_field.items():
                    field_data = all_tracking_domain_fields.get(field_name, False)
                    if field_data and not record.filtered_domain(
                        literal_eval(field_data["tracking_domain"])
                    ):
                        fields_to_remove.append(field_name)
                for field_name in fields_to_remove:
                    del model_data[record_id][field_name]
                if not model_data[record_id]:
                    record_to_remove.append(record_id)

            for record_id in record_to_remove:
                del model_data[record_id]
        return super()._tm_post_message(data)

    def _mail_track(self, tracked_fields, initial_values):
        changes, tracking_value_ids = super()._mail_track(
            tracked_fields, initial_values
        )

        # TODO: add properties support on domain filters
        tracking_value_field_ids = [
            tracking_value_id[2]["field_id"]
            for tracking_value_id in tracking_value_ids
            if "field_id" in tracking_value_id[2]
        ]
        if tracking_value_field_ids:
            all_tracking_domain_fields = self._tm_all_tracking_domain_fields()[
                self._name
            ]

            if all_tracking_domain_fields:
                # remove entries that are not matching the tracking_domain of the field
                fields_to_remove = []
                for field_name in tracked_fields:
                    field_data = all_tracking_domain_fields.get(field_name, False)
                    if field_data and not self.filtered_domain(
                        literal_eval(field_data["tracking_domain"])
                    ):
                        fields_to_remove.append(field_data["id"])
                res_changes = []
                res_tracking_value_ids = []
                # remove values from tracking result
                for change, tracking_value_id in zip(
                    changes, tracking_value_ids, strict=True
                ):
                    if tracking_value_id[2]["field_id"] not in fields_to_remove:
                        res_changes.append(change)
                        res_tracking_value_ids.append(tracking_value_id)
                changes = res_changes
                tracking_value_ids = res_tracking_value_ids
        return changes, tracking_value_ids
