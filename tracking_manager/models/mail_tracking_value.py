# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import html2plaintext


class MailTracking(models.Model):
    _inherit = "mail.tracking.value"

    # TODO: Remove if merged https://github.com/odoo/odoo/pull/156236
    def _create_tracking_values_property(
        self, initial_value, new_value, col_name, col_info, record
    ):
        field = self.env["ir.model.fields"]._get(record._name, col_name)
        field_info = {
            "desc": f"{field.field_description}: {col_info['string']}",
            "name": col_name,
            "type": col_info["type"],
        }
        if col_info["type"] in ("many2one", "many2many"):
            comodel = self.env[col_info["comodel"]]
            initial_value = comodel.browse(initial_value) if initial_value else False
            new_value = comodel.browse(new_value) if new_value else False
        values = self.env["mail.tracking.value"]._create_tracking_values(
            initial_value, new_value, col_name, col_info, record
        )
        del values["field_id"]
        return {**values, "field_info": field_info}

    @api.model
    def _create_tracking_values(
        self, initial_value, new_value, col_name, col_info, record
    ):
        try:
            return super()._create_tracking_values(
                initial_value, new_value, col_name, col_info, record
            )
        except NotImplementedError:
            if col_info["type"] == "html":
                field = self.env["ir.model.fields"]._get(record._name, col_name)
                values = {"field_id": field.id}
                values.update(
                    {
                        "old_value_char": html2plaintext(initial_value) or "",
                        "new_value_char": html2plaintext(new_value) or "",
                    }
                )
                return values
            elif col_info["type"] == "properties":
                # TODO: Remove if merged https://github.com/odoo/odoo/pull/156236
                # A return is necessary to avoid the NotImplementedError error
                field = self.env["ir.model.fields"]._get(record._name, col_name)
                return {"field_id": field.id}
            elif col_info["type"] == "tags":
                # TODO: Remove if merged https://github.com/odoo/odoo/pull/156236
                field = self.env["ir.model.fields"]._get(record._name, col_name)
                return {
                    "field_id": field.id,
                    "old_value_char": (
                        ", ".join(value for value in initial_value)
                        if initial_value
                        else ""
                    ),
                    "new_value_char": (
                        ", ".join(value for value in new_value) if new_value else ""
                    ),
                }
            raise
        except TypeError:
            # remove when https://github.com/odoo/odoo/pull/214121 is merged
            field = self.env["ir.model.fields"]._get(record._name, col_name)
            model_name = self.env._(self.env["ir.model"]._get(field.model).display_name)
            values = {"field_id": field.id}
            if col_info["type"] in {"one2many", "many2many"}:
                values.update(
                    {
                        "old_value_char": ", ".join(
                            value.display_name
                            or self.env._(
                                "Unnamed %(record_model_name)s (%(record_id)s)",
                                record_model_name=model_name,
                                record_id=value.id,
                            )
                            for value in initial_value
                        )
                        if initial_value
                        else "",
                        "new_value_char": ", ".join(
                            value.display_name
                            or self.env._(
                                "Unnamed %(record_model_name)s (%(record_id)s)",
                                record_model_name=model_name,
                                record_id=value.id,
                            )
                            for value in new_value
                        )
                        if new_value
                        else "",
                    }
                )
                return values
            raise
