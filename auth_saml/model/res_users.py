# -*- encoding: utf-8 -*-
import logging
# this is our very own dependency
import lasso
# this is an odoo8 dep so it should be present 'by default'
import passlib

import openerp
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class res_users(osv.Model):
    _inherit = 'res.users'

    _columns = {
        'saml_provider_id': fields.many2one(
            'auth.saml.provider',
            string='SAML Provider',
        ),
        'saml_uid': fields.char(
            'SAML User ID',
            help="SAML Provider user_id",
        ),
    }

    def _no_password_with_saml(self, cr, uid, ids, context=None):
        """Ensure no Odoo user posesses both an SAML user ID and an Odoo
        password.
        """

        if self._allow_saml_uid_and_internal_password(cr, uid, context):
            # The constraint is a no-op in this case.
            return True

        users = self.browse(cr, uid, ids, context=context)
        for user in users:
            if user.password and user.saml_uid:
                return False

        return True

    _constraints = [
        (
            _no_password_with_saml,
            (
                'SAML2 authentication: An Odoo user cannot possess both a '
                'SAML user ID and an Odoo password.'
            ),
            ['password', 'saml_uid']
        ),
    ]

    _sql_constraints = [
        (
            'uniq_users_saml_provider_saml_uid',
            'unique(saml_provider_id, saml_uid)',
            'SAML UID must be unique per provider'
        ),
    ]

    def _auth_saml_validate(self, cr, uid, provider_id, token, context=None):
        """ return the validation data corresponding to the access token """

        p = self.pool.get('auth.saml.provider')
        # we are not yet logged in, so the userid cannot have access to the
        # fields we need yet
        login = p._get_lasso_for_provider(
            cr, SUPERUSER_ID, provider_id, context=context
        )

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
        validation = {'user_id': login.assertion.subject.nameId.content}

        """
        if p.data_endpoint:
            data = self._auth_oauth_rpc(cr, uid, p.data_endpoint, access_token)
            validation.update(data)
        """

        return validation

    def _auth_saml_signin(
        self, cr, uid, provider, validation, saml_response, context=None
    ):
        """ retrieve and sign into openerp the user corresponding to provider
        and validated access token

            :param provider: saml provider id (int)
            :param validation: result of validation of access token (dict)
            :param saml_response: saml parameters response from the IDP
            :return: user login (str)
            :raise: openerp.exceptions.AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        token_osv = self.pool.get('auth_saml.token')
        saml_uid = validation['user_id']

        user_ids = self.search(
            cr, uid,
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

        # browse the user because we'll need this in the response
        user = self.browse(cr, uid, user_ids[0], context=context)

        user_id = user.id

        # now find if a token for this user/provider already exists
        token_ids = token_osv.search(
            cr, uid,
            [
                ('saml_provider_id', '=', provider),
                ('user_id', '=', user_id),
            ]
        )
        if token_ids:
            token_osv.write(
                cr, uid, token_ids,
                {'saml_access_token': saml_response},
                context=context
            )
        else:
            token_osv.create(
                cr, uid,
                {
                    'saml_access_token': saml_response,
                    'saml_provider_id': provider,
                    'user_id': user_id,
                },
                context=context
            )

        return user.login

    def auth_saml(self, cr, uid, provider, saml_response, context=None):

        validation = self._auth_saml_validate(
            cr, uid, provider, saml_response
        )

        # required check
        if not validation.get('user_id'):
            raise openerp.exceptions.AccessDenied()

        # retrieve and sign in user
        login = self._auth_saml_signin(
            cr, uid, provider, validation, saml_response, context=context
        )

        if not login:
            raise openerp.exceptions.AccessDenied()

        # return user credentials
        return cr.dbname, login, saml_response

    def check_credentials(self, cr, uid, token):
        """token can be a password if the user has used the normal form...
        but we are more interested in the case when they are tokens
        and the interesting code is inside the except clause
        """
        token_osv = self.pool.get('auth_saml.token')
        try:
            super(res_users, self).check_credentials(cr, uid, token)

        except (openerp.exceptions.AccessDenied, passlib.exc.PasswordSizeError):
            # since normal auth did not succeed we now try to find if the user
            # has an active token attached to his uid
            res = token_osv.search(
                cr, SUPERUSER_ID,
                [
                    ('user_id', '=', uid),
                    ('saml_access_token', '=', token),
                ]
            )

            # if the user is not found we re-raise the AccessDenied
            if not res:
                # TODO: maybe raise a defined exception instead of the last
                # exception that occurred in our execution frame
                raise

    def write(self, cr, uid, ids, vals, context=None):
        """Override to clear out the user's password when setting an SAML user
        ID (as they can't cohabit).
        """

        if vals and vals.get('saml_uid'):
            if not self._allow_saml_uid_and_internal_password(cr, uid, context):
                vals['password'] = False

        return super(res_users, self).write(
            cr, uid, ids, vals, context=context
        )

    def _allow_saml_uid_and_internal_password(self, cr, uid, context):

        # super user is always allowed to have a password in the database
        # as opposed to other users... Doing so avoids being locked out
        # of your own instance in case there is an issue with your IDP
        if uid == SUPERUSER_ID:
            return true
        setting_obj = self.pool['base.config.settings']
        return setting_obj.allow_saml_uid_and_internal_password(
            cr, uid, context=context
        )
