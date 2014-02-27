import logging
import lasso

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
        'saml_access_token': fields.char(
            'Current SAML token for this user',
            help="The current SAML token in use",
        ),
    }

    _sql_constraints = [
        (
            'uniq_users_saml_provider_saml_uid',
            'unique(saml_provider_id, saml_uid)',
            'SAML UID must be unique per provider'
        ),
    ]

    def _auth_saml_validate(self, cr, uid, provider, token, context=None):
        """ return the validation data corresponding to the access token """

        p = self.pool.get('auth.saml.provider')
        login = p._get_lasso_for_provider(cr, uid, provider, context=context)

        try:
            login.processAuthnResponseMsg(token)
        except (lasso.DsError, lasso.ProfileCannotVerifySignatureError):
            raise Exception('Lasso Profile cannot verify signature')
        except lasso.Error, e:
            raise Exception(repr(e))

        try:
            login.acceptSso()
        except lasso.Error:
            raise Exception('Invalid assertion')

        # TODO use a real token validation from LASSO
        validation = {}

        # TODO push into the validation result a real UPN
        validation['user_id'] = login.assertion.subject.nameId.content

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
            :param params: saml parameters (dict)
            :return: user login (str)
            :raise: openerp.exceptions.AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
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

        user = self.browse(cr, uid, user_ids[0], context=context)
        user.write({'saml_access_token': saml_response})

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
        return (cr.dbname, login, saml_response)

    def check_credentials(self, cr, uid, token):
        """token can be a password if the user has used the normal form...
        but we are more interested in the case when they are tokens
        and the interesting code is inside the except clause
        """
        try:
            return super(res_users, self).check_credentials(cr, uid, token)

        except openerp.exceptions.AccessDenied:
            res = self.search(
                cr, SUPERUSER_ID,
                [
                    ('id', '=', uid),
                    ('saml_access_token', '=', token),
                ]
            )

            if not res:
                # TODO: maybe raise a defined exception instead of the last
                # exception that occured in our execution frame
                raise
