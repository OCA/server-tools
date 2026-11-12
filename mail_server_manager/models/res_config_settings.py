# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mail_server_manager_domain = fields.Char(
        string="Mail Domain",
        config_parameter="mail_server_manager.mail_domain",
        default="figacycles.com",
    )
    mail_server_manager_config_path = fields.Char(
        string="Mail Config Path",
        config_parameter="mail_server_manager.config_path",
        default="/etc/odoo/mail_config",
    )
    mail_server_manager_smtp_host = fields.Char(
        string="SMTP Host",
        config_parameter="mail_server_manager.smtp_host",
        default="mail",
        help="SMTP server host",
    )
    mail_server_manager_imap_host = fields.Char(
        string="IMAP Host",
        config_parameter="mail_server_manager.imap_host",
        default="mail",
        help="IMAP server host",
    )
    mail_server_manager_imap_port = fields.Integer(
        string="IMAP Port",
        config_parameter="mail_server_manager.imap_port",
        default=993,
    )
    mail_server_manager_auto_create = fields.Boolean(
        string="Create Mailbox by Default",
        config_parameter="mail_server_manager.auto_create",
        default=False,
        help="If enabled, a mailbox will be created by default for new users",
    )
    mail_server_manager_overwrite_email = fields.Boolean(
        string="Overwrite User Email",
        config_parameter="mail_server_manager.overwrite_email",
        default=False,
        help="If enabled, creating a mailbox will overwrite the user's existing email. "
        "If disabled, the user's personal email is preserved and the internal email "
        "is only used for sending via the SMTP server.",
    )
    mail_server_manager_daily_email_limit = fields.Integer(
        string="Default Daily Email Limit",
        config_parameter="mail_server_manager.daily_email_limit",
        default=100,
        help="Default maximum number of emails a user can send per day. "
        "Set to 0 for unlimited. Can be overridden per account.",
    )
    mail_server_manager_smtp_port = fields.Integer(
        string="SMTP Port",
        config_parameter="mail_server_manager.smtp_port",
        default=587,
        help="SMTP server port (587 for STARTTLS, 465 for SSL)",
    )
    mail_server_manager_smtp_encryption = fields.Selection(
        [
            ("none", "None"),
            ("starttls", "STARTTLS"),
            ("ssl", "SSL/TLS"),
        ],
        string="SMTP Encryption",
        config_parameter="mail_server_manager.smtp_encryption",
        default="starttls",
        help="Encryption type for SMTP connection",
    )
    mail_server_manager_imap_encryption = fields.Selection(
        [
            ("none", "None"),
            ("ssl", "SSL/TLS"),
        ],
        string="IMAP Encryption",
        config_parameter="mail_server_manager.imap_encryption",
        default="ssl",
        help="Encryption type for IMAP connection",
    )
