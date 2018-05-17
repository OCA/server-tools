# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import _, http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)

try:
    from email_validator import validate_email, EmailSyntaxError
except ImportError:
    # TODO Remove in v12, dropping backwards compatibility with validate_email
    # pragma: no-cover
    try:
        from validate_email import validate_email as _validate

        class EmailSyntaxError(Exception):
            message = False

        def validate_email(*args, **kwargs):
            if not _validate(*args, **kwargs):
                raise EmailSyntaxError

    except ImportError:
        _logger.debug("Cannot import `email_validator`.")
    else:
        _logger.warning("Install `email_validator` to get full support.")


class SignupVerifyEmail(AuthSignupHome):
    @http.route()
    def web_auth_signup(self, *args, **kw):
        if (http.request.params.get("login") and
                not http.request.params.get("password")):
            return self.passwordless_signup(http.request.params)
        else:
            return super(SignupVerifyEmail, self).web_auth_signup(*args, **kw)

    def passwordless_signup(self, values):
        qcontext = self.get_auth_signup_qcontext()

        # Check good format of e-mail
        try:
            validate_email(values.get("login", ""))
        except EmailSyntaxError as error:
            qcontext["error"] = getattr(
                error,
                "message",
                _("That does not seem to be an email address."),
            )
            return http.request.render("auth_signup.signup", qcontext)
        if not values.get("email"):
            values["email"] = values.get("login")

        # Remove password
        values["password"] = ""
        sudo_users = (http.request.env["res.users"]
                      .with_context(create_user=True).sudo())

        try:
            with http.request.cr.savepoint():
                sudo_users.signup(values, qcontext.get("token"))
                sudo_users.reset_password(values.get("login"))
        except Exception as error:
            # Duplicate key or wrong SMTP settings, probably
            _logger.exception(error)

            # Agnostic message for security
            qcontext["error"] = _(
                "Something went wrong, please try again later or contact us.")
            return http.request.render("auth_signup.signup", qcontext)

        qcontext["message"] = _("Check your email to activate your account!")
        return http.request.render("auth_signup.reset_password", qcontext)
