from openerp.osv import osv, fields
import lasso
import simplejson


class auth_saml_provider(osv.osv):
    """Class defining the configuration values of an Saml2 provider"""

    _name = 'auth.saml.provider'
    _description = 'SAML2 provider'
    _order = 'name'

    def _get_lasso_for_provider(self, cr, uid, provider_id, context=None):
        #print cr, uid, provider_id, context
        provider = self.browse(cr, uid, provider_id, context=context)

        # TODO: we should cache those results somewhere because it is
        # really costy to always recreate a login variable from buffers
        server = lasso.Server.newFromBuffers(
            provider.sp_metadata,
            provider.sp_pkey
        )
        server.addProviderFromBuffer(
            lasso.PROVIDER_ROLE_IDP,
            provider.idp_metadata
        )
        return lasso.Login(server)

    def _get_auth_request(self, cr, uid, id_, state, context=None):
        """build an authentication request and give it back to our client
        WARNING: this method cannot be used for multiple ids
        """
        login = self._get_lasso_for_provider(cr, uid, id_, context=context)

        # ! -- this is the part that MUST be performed on each call and
        # cannot be cached
        login.initAuthnRequest()
        login.request.nameIdPolicy.format = None
        login.request.nameIdPolicy.allowCreate = True
        login.msgRelayState = simplejson.dumps(state)
        login.buildAuthnRequestMsg()

        # msgUrl is a fully encoded url ready for redirect use
        # obtained after the buildAuthnRequestMsg() call
        return login.msgUrl

    _columns = {
        # Name of the OAuth2 entity, authentic, xcg...
        'name': fields.char('Provider name'),
        'idp_metadata': fields.text('IDP Configuration'),
        'sp_metadata': fields.text('SP Configuration'),
        'sp_pkey': fields.text(
            'Private key of our service provider (this openerpserver)'
        ),
        'enabled': fields.boolean('Allowed'),
        'css_class': fields.char('CSS class'),
        'body': fields.char('Body'),
        'sequence': fields.integer(),
    }

    _defaults = {
        'enabled': False,
    }
