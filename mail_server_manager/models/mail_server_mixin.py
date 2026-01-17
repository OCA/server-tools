# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailServerManagerMixin(models.AbstractModel):
    """Mixin providing common configuration methods for mail_server_manager.

    This centralizes configuration access and adds caching for performance.
    """

    _name = "mail.server.manager.mixin"
    _description = "Mail Server Manager Configuration Mixin"

    @api.model
    def _get_mail_domain(self):
        """Get the mail domain from configuration (cached)."""
        return self._get_cached_param(
            "mail_server_manager.mail_domain", "figacycles.com"
        )

    @api.model
    def _get_mail_config_path(self):
        """Get the mail configuration path with validation."""
        path = self._get_cached_param(
            "mail_server_manager.config_path", "/etc/odoo/mail_config"
        )
        # Security: validate path is within allowed directories
        if not self._validate_config_path(path):
            _logger.warning("Invalid config_path: %s, using default", path)
            return "/etc/odoo/mail_config"
        return path

    @api.model
    def _get_smtp_host(self):
        """Get SMTP host from configuration (cached)."""
        return self._get_cached_param("mail_server_manager.smtp_host", "mail")

    @api.model
    def _get_imap_host(self):
        """Get IMAP host from configuration (cached)."""
        return self._get_cached_param("mail_server_manager.imap_host", "mail")

    @api.model
    def _get_imap_port(self):
        """Get IMAP port from configuration (cached)."""
        return int(self._get_cached_param("mail_server_manager.imap_port", 993))

    @api.model
    def _get_auto_create_mailbox(self):
        """Check if auto-create mailbox is enabled (cached)."""
        return (
            self._get_cached_param("mail_server_manager.auto_create", "False") == "True"
        )

    @api.model
    def _get_overwrite_email(self):
        """Check if overwrite email is enabled (cached)."""
        return (
            self._get_cached_param("mail_server_manager.overwrite_email", "False")
            == "True"
        )

    @api.model
    def _get_cached_param(self, key, default):
        """Get a system parameter with caching.

        Uses a simple cache that clears on registry reload.
        """
        cache_key = f"_mail_server_manager_cache_{key}"

        # Check thread-local cache
        if not hasattr(self.env, cache_key):
            value = self.env["ir.config_parameter"].sudo().get_param(key, default)
            setattr(self.env, cache_key, value)

        return getattr(self.env, cache_key)

    @api.model
    def _validate_config_path(self, path):
        """Validate that config path is safe and within allowed directories.

        Security measure to prevent path traversal attacks.
        """
        if not path:
            return False

        # Normalize path
        try:
            normalized = os.path.normpath(path)
        except Exception:
            return False

        # Check for path traversal attempts
        if ".." in normalized:
            return False

        # Allowed base paths
        allowed_bases = ["/etc/odoo", "/var/lib/odoo", "/mnt"]

        return any(normalized.startswith(base) for base in allowed_bases)

    @api.model
    def _clear_param_cache(self):
        """Clear the parameter cache. Call after config changes."""
        keys = [
            "mail_domain",
            "config_path",
            "smtp_host",
            "imap_host",
            "imap_port",
            "auto_create",
            "overwrite_email",
        ]
        for key in keys:
            cache_key = f"_mail_server_manager_cache_mail_server_manager.{key}"
            if hasattr(self.env, cache_key):
                delattr(self.env, cache_key)
