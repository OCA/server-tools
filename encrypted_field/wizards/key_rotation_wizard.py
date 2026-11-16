import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config

_logger = logging.getLogger(__name__)


class KeyRotationWizard(models.TransientModel):
    """Wizard for rotating encryption keys."""

    _name = "pb.key.rotation.wizard"
    _description = "Encryption Key Rotation Wizard"

    new_key = fields.Char(
        required=True,
        help="The new encryption key to rotate to",
    )
    generate_new_key = fields.Boolean(
        default=True,
        help="Automatically generate a secure new key",
    )
    state = fields.Selection(
        [
            ("draft", "Configure"),
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
        """Auto-generate a new key by default."""
        res = super().default_get(fields_list)
        if "new_key" in fields_list and res.get("generate_new_key", True):
            try:
                from cryptography.fernet import Fernet

                res["new_key"] = Fernet.generate_key().decode()
            except ImportError:
                _logger.warning("cryptography package not installed")
        return res

    def _get_current_key(self):
        """Get the current encryption key from config."""
        key = config.get("encryption_key")
        if not key:
            raise UserError(_("No encryption key configured in odoo.conf"))
        return key

    @api.onchange("generate_new_key")
    def _onchange_generate_new_key(self):
        if self.generate_new_key:
            try:
                from cryptography.fernet import Fernet

                self.new_key = Fernet.generate_key().decode()
            except ImportError as err:
                raise UserError(_("cryptography package not installed")) from err

    def _get_encrypted_fields(self):
        """Find all encrypted fields in all models."""
        from ..fields.encrypted import Encrypted

        encrypted_fields = []

        for model_name, model in self.env.registry.items():
            if model._abstract or model._transient:
                continue
            for field_name, field in model._fields.items():
                if isinstance(field, Encrypted):
                    encrypted_fields.append(
                        {
                            "model": model_name,
                            "field": field_name,
                        }
                    )

        return encrypted_fields

    def action_preview(self):
        """Preview what will be rotated."""
        self.ensure_one()

        # Validate keys
        try:
            from cryptography.fernet import Fernet

            old_key = self._get_current_key()
            Fernet(old_key.encode())  # Validate old key
            Fernet(self.new_key.encode())  # Validate new key
        except Exception as e:
            raise UserError(
                _("Invalid key format: %(error)s") % {"error": str(e)}
            ) from e

        # Find all encrypted fields
        encrypted_fields = self._get_encrypted_fields()

        if not encrypted_fields:
            self.preview_info = _("No encrypted fields found in the database.")
            self.state = "preview"
            return self._reopen()

        # Count records
        preview_lines = []
        total_records = 0

        for ef in encrypted_fields:
            try:
                # Use direct SQL to count - avoids ORM search restrictions
                table = self.env[ef["model"]]._table
                field = ef["field"]
                self.env.cr.execute(
                    f'SELECT COUNT(*) FROM "{table}" '
                    f'WHERE "{field}" IS NOT NULL AND "{field}" != %s',
                    ("",),
                )
                count = self.env.cr.fetchone()[0]
                if count > 0:
                    preview_lines.append(
                        f"  - {ef['model']}.{ef['field']}: {count} records"
                    )
                    total_records += count
            except Exception as e:
                preview_lines.append(
                    f"  - {ef['model']}.{ef['field']}: Error counting - {e}"
                )

        self.preview_info = _(
            "Key Rotation Preview\n"
            "====================\n\n"
            "Encrypted fields found:\n%(fields)s\n\n"
            "Total records to process: %(total)d\n\n"
            "The wizard will:\n"
            "1. Re-encrypt all data with the new key\n"
            "2. Update odoo.conf with the new key\n"
            "3. Activate the new key in memory (no restart needed)\n\n"
            "WARNING: Back up your database before proceeding!"
        ) % {
            "fields": "\n".join(preview_lines) if preview_lines else "  None",
            "total": total_records,
        }

        self.state = "preview"
        return self._reopen()

    def _update_config_file(self, new_key):
        """Update the encryption_key in odoo.conf."""
        config_file = config.rcfile
        if not config_file:
            return False, "No config file path found"

        try:
            with open(config_file) as f:
                content = f.read()

            # Replace existing encryption_key or add it
            if re.search(r"^encryption_key\s*=", content, re.MULTILINE):
                new_content = re.sub(
                    r"^encryption_key\s*=.*$",
                    f"encryption_key = {new_key}",
                    content,
                    flags=re.MULTILINE,
                )
            else:
                # Add to end of file
                new_content = content.rstrip() + f"\nencryption_key = {new_key}\n"

            with open(config_file, "w") as f:
                f.write(new_content)

            return True, config_file

        except Exception as e:
            return False, str(e)

    def _bump_key_version(self):
        """Bump the key version so all workers reload the key from config."""
        from ..fields.encrypted import bump_key_version

        bump_key_version(self.env)

    def action_rotate(self):
        """Execute key rotation."""
        self.ensure_one()

        try:
            from cryptography.fernet import Fernet

            old_key = self._get_current_key()
            old_fernet = Fernet(old_key.encode())
            new_fernet = Fernet(self.new_key.encode())
        except Exception as e:
            raise UserError(
                _("Invalid key format: %(error)s") % {"error": str(e)}
            ) from e

        encrypted_fields = self._get_encrypted_fields()
        results = []
        total_success = 0
        total_failed = 0

        for ef in encrypted_fields:
            model_name = ef["model"]
            field_name = ef["field"]
            table = self.env[model_name]._table

            try:
                # Get records with encrypted data via SQL
                self.env.cr.execute(
                    f'SELECT id, "{field_name}" FROM "{table}" '
                    f'WHERE "{field_name}" IS NOT NULL AND "{field_name}" != %s',
                    ("",),
                )
                rows = self.env.cr.fetchall()

                success = 0
                failed = 0

                for record_id, encrypted_value in rows:
                    try:
                        # Decrypt with old key
                        decrypted = old_fernet.decrypt(
                            encrypted_value.encode()
                        ).decode()

                        # Re-encrypt with new key
                        new_encrypted = new_fernet.encrypt(decrypted.encode()).decode()

                        # Update directly in DB
                        self.env.cr.execute(
                            f'UPDATE "{table}" SET "{field_name}" = %s WHERE id = %s',
                            (new_encrypted, record_id),
                        )

                        success += 1

                    except Exception as e:
                        _logger.error(
                            "Failed to rotate key for %s.%s record %s: %s",
                            model_name,
                            field_name,
                            record_id,
                            e,
                        )
                        failed += 1

                if success > 0 or failed > 0:
                    results.append(
                        f"  - {model_name}.{field_name}: "
                        f"{success} success, {failed} failed"
                    )
                    total_success += success
                    total_failed += failed

            except Exception as e:
                results.append(f"  - {model_name}.{field_name}: Error - {e}")
                _logger.error("Failed to process %s.%s: %s", model_name, field_name, e)

        # Only proceed with config/memory update if we had success and no failures
        if total_failed > 0:
            # Rollback - don't update config if there were failures
            self.env.cr.rollback()
            self.result_info = _(
                "Key Rotation FAILED\n"
                "===================\n\n"
                "Errors occurred during rotation. Database has been rolled back.\n"
                "Your original key is still valid.\n\n"
                "Results:\n%(results)s\n\n"
                "Total: %(attempted)d attempted, %(failed)d failed\n\n"
                "Fix the errors and try again."
            ) % {
                "results": "\n".join(results) if results else "  No fields processed",
                "attempted": total_success + total_failed,
                "failed": total_failed,
            }
            self.state = "done"
            return self._reopen()

        # Commit database changes first
        # pylint: disable=invalid-commit
        # Key rotation requires explicit commit to ensure data is persisted
        # before updating config file with the new key
        self.env.cr.commit()

        # Clear ORM caches
        self.env.registry.clear_cache()

        # Only update config AFTER successful database commit
        config_updated, config_result = self._update_config_file(self.new_key)

        # Bump version so all workers reload key from config file
        self._bump_key_version()

        if config_updated:
            config_msg = f"Config file updated: {config_result}"
        else:
            config_msg = (
                f"Could not update config file: {config_result}\n"
                "You must manually update encryption_key in odoo.conf"
            )

        self.result_info = _(
            "Key Rotation Complete\n"
            "=====================\n\n"
            "Results:\n%(results)s\n\n"
            "Total: %(rotated)d records rotated, %(failed)d failed\n\n"
            "%(config_msg)s\n\n"
            "The new key is now active in memory. No restart required."
        ) % {
            "results": "\n".join(results) if results else "  No records processed",
            "rotated": total_success,
            "failed": total_failed,
            "config_msg": config_msg,
        }

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
