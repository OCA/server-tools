# Copyright 2018-2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Configuration of Letsencrypt."""

from odoo import _, api, exceptions, fields, models

DNS_SCRIPT_DEFAULT = """# Write your script here
# It should create a TXT record of $LETSENCRYPT_DNS_CHALLENGE
# on _acme-challenge.$LETSENCRYPT_DNS_DOMAIN
"""


class ResConfigSettings(models.TransientModel):
    """Configuration of Letsencrypt."""

    _inherit = "res.config.settings"

    letsencrypt_altnames = fields.Char(
        string="Domain names",
        default="",
        help=(
            "Domains to use for the certificate. " "Separate with commas or newlines."
        ),
        config_parameter="letsencrypt.altnames",
    )
    letsencrypt_dns_provider = fields.Selection(
        selection=[("shell", "Shell script")],
        string="DNS provider",
        help=(
            "For wildcard certificates we need to add a TXT record on your "
            'DNS. If you set this to "Shell script" you can enter a shell '
            "script. Other options can be added by installing additional "
            "modules."
        ),
        config_parameter="letsencrypt.dns_provider",
    )
    letsencrypt_dns_shell_script = fields.Char(
        string="DNS update script",
        help=(
            "Write a shell script that will update your DNS TXT records. "
            "You can use the $LETSENCRYPT_DNS_CHALLENGE and "
            "$LETSENCRYPT_DNS_DOMAIN variables."
        ),
        default=DNS_SCRIPT_DEFAULT,
        config_parameter="letsencrypt.dns_shell_script",
    )
    letsencrypt_needs_dns_provider = fields.Boolean()
    letsencrypt_reload_command = fields.Char(
        string="Server reload command",
        help="Fill this with the command to restart your web server.",
        config_parameter="letsencrypt.reload_command",
    )
    letsencrypt_testing_mode = fields.Boolean(
        string="Use testing server",
        help=(
            "Use the Let's Encrypt staging server, which has higher rate "
            "limits but doesn't create valid certificates."
        ),
        config_parameter="letsencrypt.testing_mode",
    )
    letsencrypt_prefer_dns = fields.Boolean(
        string="Prefer DNS validation",
        help=(
            "Validate through DNS even when HTTP validation is possible. "
            "Use this if your Odoo instance isn't publicly accessible."
        ),
        config_parameter="letsencrypt.prefer_dns",
    )

    @api.onchange("letsencrypt_altnames", "letsencrypt_prefer_dns")
    def letsencrypt_check_dns_required(self):
        """Check wether DNS required for Letsencrypt."""
        altnames = self.letsencrypt_altnames or ""
        self.letsencrypt_needs_dns_provider = (
            "*." in altnames or self.letsencrypt_prefer_dns
        )

    def set_values(self):
        """Set Letsencrypt values on settings object."""
        result = super().set_values()
        self.letsencrypt_check_dns_required()
        if self.letsencrypt_dns_provider == "shell":
            lines = [
                line.strip() for line in self.letsencrypt_dns_shell_script.split("\n")
            ]
            if all(line == "" or line.startswith("#") for line in lines):
                raise exceptions.ValidationError(
                    _("You didn't write a DNS update script!")
                )
        return result
