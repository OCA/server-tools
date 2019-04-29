# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring,invalid-name
import logging

from odoo import _, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_reset_password(self):
        """Disable password reset for ldap users."""
        template = self.env.ref('users_ldap_no_reset.no_reset_password_email')
        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False}
        template.write(template_values)
        for this in self:
            if not this.email:
                raise UserError(
                    _("Cannot send email: user %s has no email address.") %
                    this.name)
            if not this.ldap_id:
                # not an ldap user
                super(ResUsers, this).action_reset_password()
                continue
            with self.env.cr.savepoint():
                template.with_context(
                    lang=this.lang).send_mail(
                        this.id, force_send=True, raise_exception=True)
            _logger.info(
                "Password reset not allowed email sent for user <%s> to <%s>",
                this.login, this.email)
