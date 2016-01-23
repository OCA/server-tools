# -*- coding: utf-8 -*-

import logging
# this is our very own dependency
import lasso
# this is an odoo8 dep so it should be present 'by default'
import passlib

import openerp
from openerp import api
from openerp import models
from openerp import fields
from openerp import SUPERUSER_ID
from openerp.exceptions import ValidationError
from openerp import _

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    saml_provider_id = fields.Many2one(
        'auth.saml.provider',
        string='SAML Provider',
    )
    saml_uid = fields.Char(
        'SAML User ID',
        help="SAML Provider user_id",
    )

    @api.multi
    @api.constrains('password_crypt', 'password', 'saml_uid')
    def check_no_password_with_saml(self):
        """Ensure no Odoo user posesses both an SAML user ID and an Odoo
        password. Except admin which is not constrained by this rule.
        """
        self.ensure_one()
        if self._allow_saml_and_password():
            pass

        else:
            # Super admin is the only user we allow to have a local password
            # in the database
            if (

                (self.password or self.password_crypt) and
                self.saml_uid and
                self.id is not SUPERUSER_ID
            ):
                raise ValidationError(
                    _("This database disallows users to have both passwords "
                      "and SAML IDs. Errors for login %s" % (self.login)
                      )
                )

    _sql_constraints = [
        (
            'uniq_users_saml_provider_saml_uid',
            'unique(saml_provider_id, saml_uid)',
            'SAML UID must be unique per provider'
        ),
    ]

    @api.multi
    def _auth_saml_validate(self, provider_id, token):
        """ return the validation data corresponding to the access token """

        pobj = self.env['auth.saml.provider']
        p = pobj.browse(provider_id)

        # we are not yet logged in, so the userid cannot have access to the
        # fields we need yet
        login = p.sudo()._get_lasso_for_provider()

        try:
            login.processAuthnResponseMsg(token)
        except (lasso.DsError, lasso.ProfileCannotVerifySignatureError):
            raise Exception('Lasso Profile cannot verify signature')
        except lasso.ProfileStatusNotSuccessError:
            raise Exception('Profile Status Not Success Error')
        except lasso.Error, e:
            raise Exception(repr(e))

        try:
            login.acceptSso()
        except lasso.Error:
            raise Exception('Invalid assertion')

        # TODO use a real token validation from LASSO
        # TODO push into the validation result a real UPN
        return {'user_id': login.assertion.subject.nameId.content}

    @api.multi
    def _auth_saml_signin(self, provider, validation, saml_response):
        """ retrieve and sign into openerp the user corresponding to provider
        and validated access token

            :param provider: saml provider id (int)
            :param validation: result of validation of access token (dict)
            :param saml_response: saml parameters response from the IDP
            :return: user login (str)
            :raise: openerp.exceptions.AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        token_osv = self.env['auth_saml.token']
        saml_uid = validation['user_id']

        user_ids = self.search(
            [
                ("saml_uid", "=", saml_uid),
                ('saml_provider_id', '=', provider),
            ]
        )

        if not user_ids:
            raise openerp.exceptions.AccessDenied()

        # TODO replace assert by proper raise... asserts do not execute in
        # production code...
        assert len(user_ids) == 1
        user = user_ids[0]

        # now find if a token for this user/provider already exists
        token_ids = token_osv.search(
            [
                ('saml_provider_id', '=', provider),
                ('user_id', '=', user.id),
            ]
        )

        if token_ids:
            token_ids.write(
                {'saml_access_token': saml_response},
            )
        else:
            token_osv.create(
                {
                    'saml_access_token': saml_response,
                    'saml_provider_id': provider,
                    'user_id': user.id,
                },
            )

        return user.login

    @api.model
    def auth_saml(self, provider, saml_response):

        validation = self._auth_saml_validate(provider, saml_response)

        # required check
        if not validation.get('user_id'):
            raise openerp.exceptions.AccessDenied()

        # retrieve and sign in user
        login = self._auth_saml_signin(provider, validation, saml_response)

        if not login:
            raise openerp.exceptions.AccessDenied()

        # return user credentials
        return self.env.cr.dbname, login, saml_response

    @api.model
    def check_credentials(self, token):
        """token can be a password if the user has used the normal form...
        but we are more interested in the case when they are tokens
        and the interesting code is inside the except clause
        """
        token_osv = self.env['auth_saml.token']
        try:
            super(ResUsers, self).check_credentials(token)
        except (
            openerp.exceptions.AccessDenied,
            passlib.exc.PasswordSizeError,
        ):
            # since normal auth did not succeed we now try to find if the user
            # has an active token attached to his uid
            res = token_osv.sudo().search(
                [
                    ('user_id', '=', self.env.uid),
                    ('saml_access_token', '=', token),
                ]
            )

            if not res:
                raise openerp.exceptions.AccessDenied()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default['saml_uid'] = False
        default['saml_provider_id'] = False
        return super(ResUsers, self).copy(default=default)

    @api.multi
    def write(self, vals):
        """Override to clear out the user's password when setting an SAML user
        ID (as they can't cohabit).
        """

        if vals and vals.get('saml_uid'):
            if not self._allow_saml_and_password() and self.id != SUPERUSER_ID:
                vals['password'] = False

        return super(ResUsers, self).write(vals)

    @api.model
    def _allow_saml_and_password(self):

        settings_obj = self.env['base.config.settings']
        return settings_obj.allow_saml_and_password()
