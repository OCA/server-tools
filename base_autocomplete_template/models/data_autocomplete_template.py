# Copyright 2026 (APSL-Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError

TECHNICAL_SKIP = {
    "id",
    "create_uid",
    "create_date",
    "write_uid",
    "write_date",
    "__last_update",
    "display_name",
}


class DataAutocompleteTemplate(models.Model):
    _name = "data.autocomplete.template"
    _description = "Data Autocomplete template (JSON defaults)"
    _order = "name"

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)

    model_id = fields.Many2one(
        "ir.model", required=True, ondelete="cascade", index=True
    )
    model = fields.Char(related="model_id.model", store=True, index=True)

    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, index=True
    )

    user_id = fields.Many2one(
        "res.users",
        string="Owner",
        help="If set, only this user can see/update it (unless admin).",
        index=True,
    )

    values_json = fields.Text(required=True)

    def get_values(self):
        """Return dict parsed from values_json (safe)."""
        self.ensure_one()
        try:
            return json.loads(self.values_json or "{}")
        except Exception:
            return {}

    def set_values(self, values: dict):
        """Store given dict as JSON in values_json."""
        self.ensure_one()
        self.values_json = json.dumps(
            values or {},
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )


class DataTemplateMixin(models.AbstractModel):
    """Generic JSON template mixin.

    Add this mixin to any wizard/model to get:
      - template_id field (select a template)
      - actions:
          * action_open_create_template_wizard()
          * action_update_current_template()
          * action_apply_template()

    The mixin stores templates in model `data.autocomplete.template` with a JSON dict.

    Hooks you can override in your wizard/model:
      - _template_skip_fields(): set of field names to never store/apply
      - _template_driver_fields(): fields applied first (to satisfy onchanges/domains)
      - _template_protected_fields(): fields re-applied last to avoid being
      cleared by onchanges
      - _template_domain_extra(): add extra domain to template selection
      (e.g. filter by report_id)
      - _template_allow_field(field_name, field): fine-grained allow/deny logic

    Onchange-friendly application:
      The mixin applies values in 3 phases:
        1) drivers
        2) the rest
        3) protected (wins last)
      and sets context key `apply_template=True` while writing,
      so you can skip destructive onchanges when applying a template.
    """

    _name = "data.template.mixin"
    _description = "Template Mixin (JSON)"

    template_id = fields.Many2one(
        "data.autocomplete.template",
        string="Template",
        domain=lambda self: self._template_domain(),
    )

    # -------------------------
    # Hooks
    # -------------------------
    def _template_skip_fields(self):
        return set(TECHNICAL_SKIP)

    def _template_driver_fields(self):
        return set()

    def _template_protected_fields(self):
        return set()

    def _template_domain_extra(self):
        """Override to add extra domain filters for templates (e.g. report_id)."""
        return []

    @api.model
    def _template_domain(self):
        domain = [
            ("active", "=", True),
            ("model_id.model", "=", self._name),
        ]
        # company: global (False) or current company
        domain += [
            "|",
            ("company_id", "=", False),
            ("company_id", "=", self.env.company.id),
        ]
        # owner: global (False) or current user
        domain += ["|", ("user_id", "=", False), ("user_id", "=", self.env.uid)]
        domain += self._template_domain_extra()
        return domain

    def _template_allow_field(self, field_name, field):
        if field_name in self._template_skip_fields():
            return False
        if field.type == "one2many":
            return False
        # avoid computed fields without inverse
        if getattr(field, "compute", False) and not getattr(field, "inverse", False):
            return False
        # avoid readonly fields (often non-writeable on wizards)
        if getattr(field, "readonly", False):
            return False
        return True

    # -------------------------
    # Serialize / normalize / apply
    # -------------------------
    def _template_serialize(self):
        """Return a JSON-safe dict with current values."""
        self.ensure_one()
        values = {}
        for name, field in self._fields.items():
            if not self._template_allow_field(name, field):
                continue

            val = self[name]
            if field.type == "many2one":
                values[name] = val.id if val else False
            elif field.type == "many2many":
                values[name] = val.ids
            else:
                values[name] = val
        return values

    def _template_normalize_vals(self, values: dict, overwrite=True):
        """Convert JSON values to write()-ready vals."""
        self.ensure_one()
        vals = {}
        for name, raw in (values or {}).items():
            if name not in self._fields:
                continue
            field = self._fields[name]
            if not self._template_allow_field(name, field):
                continue

            if not overwrite:
                current = self[name]
                if field.type == "many2one" and current:
                    continue
                if field.type == "many2many" and current:
                    continue
                if field.type not in ("many2one", "many2many") and current not in (
                    False,
                    None,
                    "",
                    0,
                    0.0,
                ):
                    continue

            if field.type == "many2one":
                vals[name] = int(raw) if raw else False
            elif field.type == "many2many":
                vals[name] = [(6, 0, raw or [])]
            else:
                vals[name] = raw
        return vals

    def _template_apply_phased(self, values: dict, overwrite=True):
        """Apply values in phases (drivers -> rest -> protected)."""
        self.ensure_one()
        vals = self._template_normalize_vals(values, overwrite=overwrite)
        if not vals:
            return True

        drivers = set(self._template_driver_fields() or set())
        protected = set(self._template_protected_fields() or set())
        protected -= drivers

        rec = self.with_context(apply_template=True)

        # 1) Drivers
        driver_vals = {k: v for k, v in vals.items() if k in drivers}
        if driver_vals:
            rec.write(driver_vals)

        # 2) Everything else (excluding protected)
        mid_vals = {
            k: v for k, v in vals.items() if k not in drivers and k not in protected
        }
        if mid_vals:
            rec.write(mid_vals)

        # 3) Protected last
        prot_vals = {k: v for k, v in vals.items() if k in protected}
        if prot_vals:
            rec.write(prot_vals)

        return True

    # -------------------------
    # Actions (buttons)
    # -------------------------
    def action_apply_template(self, overwrite=True):
        self.ensure_one()
        if not self.template_id:
            raise UserError(_("No template selected."))
        if self.template_id.model_id.model != self._name:
            raise UserError(_("Template model mismatch."))
        self._template_apply_phased(self.template_id.get_values(), overwrite=overwrite)
        return self._reopen_action()

    def action_open_create_template_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Save as Template"),
            "res_model": "data.wizard.template.create",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": self._name,
                "active_id": self.id,
                "default_model_id": self.env["ir.model"]._get_id(self._name),
                "default_company_id": self.env.company.id,
            },
        }

    def action_update_current_template(self):
        self.ensure_one()
        if not self.template_id:
            raise UserError(_("You must select a template to update it."))

        template = self.template_id
        if template.model_id.model != self._name:
            raise UserError(_("Template model mismatch."))

        # Do not allow updating someone else's personal template (unless admin)
        if (
            template.user_id
            and template.user_id.id != self.env.uid
            and not self.env.user._is_admin()
        ):
            raise UserError(
                _("You cannot update a personal template owned by another user.")
            )

        template.set_values(self._template_serialize())
        return self._reopen_action()

    def _reopen_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "context": dict(self.env.context),
        }
