# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """The template is noupdate: switch off default recipients on existing
    databases, otherwise email_to is ignored and the mail has no recipient."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    template = env.ref(
        "scheduler_error_mailer.scheduler_error_mailer", raise_if_not_found=False
    )
    if template:
        template.use_default_to = False
