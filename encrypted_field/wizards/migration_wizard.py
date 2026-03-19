# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MigrationWizardLine(models.TransientModel):
    """Line item for encrypted field selection."""

    _name = "pb.encryption.migration.wizard.line"
    _description = "Encryption Migration Field"

    wizard_id = fields.Many2one(
        "pb.encryption.migration.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    selected = fields.Boolean(string="Encrypt", default=False)
    model_name = fields.Char(string="Model", readonly=True)
    field_name = fields.Char(string="Field", readonly=True)
    unencrypted_count = fields.Integer(string="Unencrypted Records", readonly=True)
    display_name = fields.Char(string="Field", compute="_compute_display_name")

    @api.depends("model_name", "field_name")
    def _compute_display_name(self):
        for line in self:
            line.display_name = f"{line.model_name}.{line.field_name}"


class MigrationWizard(models.TransientModel):
    """Wizard for encrypting existing plaintext data."""

    _name = "pb.encryption.migration.wizard"
    _description = "Encrypt Existing Data Wizard"

    line_ids = fields.One2many(
        "pb.encryption.migration.wizard.line",
        "wizard_id",
        string="Encrypted Fields",
    )
    state = fields.Selection(
        [
            ("draft", "Select Fields"),
            ("preview", "Preview"),
            ("done", "Completed"),
        ],
        default="draft",
    )
    preview_info = fields.Text(
        string="Preview Information",
        readonly=True,
    )
    result_info = fields.Text(
        string="Result",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        """Auto-populate with all encrypted fields."""
        res = super().default_get(fields_list)

        if "line_ids" in fields_list:
            lines = []
            for field_info in self._get_encrypted_fields_with_counts():
                lines.append(
                    (
                        0,
                        0,
                        {
                            "model_name": field_info["model"],
                            "field_name": field_info["field"],
                            "unencrypted_count": field_info["count"],
                            "selected": field_info["count"]
                            > 0,  # Pre-select if has unencrypted data
                        },
                    )
                )
            res["line_ids"] = lines

        return res

    def _get_encrypted_fields_with_counts(self):
        """Find all encrypted fields and count unencrypted records."""
        from ..fields.encrypted import Encrypted

        result = []

        for model_name, model in self.env.registry.items():
            if model._abstract or model._transient:
                continue

            for field_name, field in model._fields.items():
                if isinstance(field, Encrypted):
                    # Count unencrypted records
                    try:
                        table = model._table
                        self.env.cr.execute(
                            f"""
                            SELECT COUNT(*) FROM "{table}"
                            WHERE "{field_name}" IS NOT NULL
                              AND "{field_name}" != ''
                              AND "{field_name}" NOT LIKE 'gA%%'
                        """
                        )
                        count = self.env.cr.fetchone()[0]
                    except Exception as e:
                        _logger.warning(
                            "Error counting %s.%s: %s", model_name, field_name, e
                        )
                        count = -1  # Indicate error

                    result.append(
                        {
                            "model": model_name,
                            "field": field_name,
                            "count": count,
                        }
                    )

        # Sort by count descending (fields needing encryption first)
        result.sort(key=lambda x: (-x["count"], x["model"], x["field"]))
        return result

    def action_refresh(self):
        """Refresh the field list and counts."""
        self.ensure_one()
        self.line_ids.unlink()

        for field_info in self._get_encrypted_fields_with_counts():
            self.env["pb.encryption.migration.wizard.line"].create(
                {
                    "wizard_id": self.id,
                    "model_name": field_info["model"],
                    "field_name": field_info["field"],
                    "unencrypted_count": field_info["count"],
                    "selected": field_info["count"] > 0,
                }
            )

        return self._reopen()

    def action_select_all(self):
        """Select all fields with unencrypted data."""
        self.line_ids.filtered(
            lambda line: line.unencrypted_count > 0
        ).write({"selected": True})
        return self._reopen()

    def action_select_none(self):
        """Deselect all fields."""
        self.line_ids.write({"selected": False})
        return self._reopen()

    def action_preview(self):
        """Preview what will be encrypted."""
        self.ensure_one()

        selected = self.line_ids.filtered("selected")
        if not selected:
            raise UserError(_("Please select at least one field to encrypt."))

        preview_lines = []
        total_records = 0

        for line in selected:
            if line.unencrypted_count > 0:
                preview_lines.append(
                    f"  - {line.model_name}.{line.field_name}: "
                    f"{line.unencrypted_count} records"
                )
                total_records += line.unencrypted_count
            elif line.unencrypted_count == 0:
                preview_lines.append(
                    f"  - {line.model_name}.{line.field_name}: already encrypted"
                )

        self.preview_info = _(
            "Encryption Preview\n"
            "==================\n\n"
            "Fields to process:\n%s\n\n"
            "Total unencrypted records: %d\n\n"
            "This will encrypt all plaintext values in-place.\n"
            "Already-encrypted values will be skipped."
        ) % ("\n".join(preview_lines), total_records)

        self.state = "preview"
        return self._reopen()

    def action_migrate(self):
        """Execute in-place encryption for selected fields."""
        self.ensure_one()

        from ..fields.encrypted import encrypt_value

        selected = self.line_ids.filtered("selected")
        if not selected:
            raise UserError(_("No fields selected."))

        results = []
        total_success = 0
        total_failed = 0

        for line in selected:
            model_name = line.model_name
            field_name = line.field_name

            try:
                table = self.env[model_name]._table

                # Fetch unencrypted records
                self.env.cr.execute(
                    f"""
                    SELECT id, "{field_name}" FROM "{table}"
                    WHERE "{field_name}" IS NOT NULL
                      AND "{field_name}" != ''
                      AND "{field_name}" NOT LIKE 'gA%%'
                """
                )
                rows = self.env.cr.fetchall()

                success = 0
                failed = 0

                for record_id, plaintext_value in rows:
                    try:
                        encrypted = encrypt_value(str(plaintext_value))
                        self.env.cr.execute(
                            f'UPDATE "{table}" SET "{field_name}" = %s WHERE id = %s',
                            [encrypted, record_id],
                        )
                        success += 1
                    except Exception as e:
                        failed += 1
                        _logger.error(
                            "Failed to encrypt %s.%s record %s: %s",
                            model_name,
                            field_name,
                            record_id,
                            e,
                        )

                if success > 0 or failed > 0:
                    results.append(
                        f"  - {model_name}.{field_name}: "
                        f"{success} encrypted, {failed} failed"
                    )
                    total_success += success
                    total_failed += failed
                else:
                    results.append(
                        f"  - {model_name}.{field_name}: no records to process"
                    )

            except Exception as e:
                results.append(f"  - {model_name}.{field_name}: Error - {e}")
                _logger.error("Failed to process %s.%s: %s", model_name, field_name, e)

        # Commit changes
        self.env.cr.commit()

        # Clear caches
        self.env.registry.clear_cache()

        self.result_info = _(
            "Encryption Complete\n"
            "===================\n\n"
            "Results:\n%s\n\n"
            "Total: %d records encrypted, %d failed"
        ) % (
            "\n".join(results) if results else "  No fields processed",
            total_success,
            total_failed,
        )

        self.state = "done"
        return self._reopen()

    def _reopen(self):
        """Reopen the wizard."""
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
