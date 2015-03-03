from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import orm


_SAML_UID_AND_PASS_SETTING = 'auth_saml.allow_saml.uid_and_internal_password'


class base_settings(orm.TransientModel):
    """Inherit from base.config.settings to add a setting. This is only here
    for easier access; the setting is not actually stored by this (transient)
    collection. Instead, it is kept in sync with the
    "auth_saml.allow_saml.uid_and_internal_password" global setting. See
    comments in the definition of the "res.config.settings" collection for
    details.
    """

    _inherit = 'base.config.settings'

    _columns = {
        'allow_saml_uid_and_internal_password': fields.boolean(
            (
                'Allow SAML users to posess an Odoo password (warning: '
                'decreases security)'
            ),
        ),
    }

    def allow_saml_uid_and_internal_password(self, cr, context=None):
        """Read the allow_saml_uid_and_internal_password setting.
        Use the admin account to bypass security restrictions.
        """

        uid = SUPERUSER_ID

        config_obj = self.pool['ir.config_parameter']

        config_ids = config_obj.search(
            cr, uid,
            [('key', '=', _SAML_UID_AND_PASS_SETTING)],
            limit=1,
            context=context
        )
        if not config_ids:
            return False

        config = config_obj.browse(
            cr, uid, config_ids, context=context
        )[0]
        return (True if config.value == '1' else False)

    def get_default_allow_saml_uid_and_internal_password(
        self, cr, uid, fields, context=None
    ):
        """Read the allow_saml_uid_and_internal_password setting. This function
        is called when the form is shown.
        """

        ret = {}

        if 'allow_saml_uid_and_internal_password' in fields:
            ret['allow_saml_uid_and_internal_password'] = (
                self.allow_saml_uid_and_internal_password(cr, context)
            )

        return ret

    def set_allow_saml_uid_and_internal_password(
        self, cr, uid, ids, context=None
    ):
        """Update the allow_saml_uid_and_internal_password setting. This
        function is called when saving the form.
        """

        dlg = self.browse(cr, uid, ids, context=context)[0]

        setting_value = (
            '1' if dlg.allow_saml_uid_and_internal_password else '0'
        )

        config_obj = self.pool['ir.config_parameter']
        config_ids = config_obj.search(
            cr, uid,
            [('key', '=', _SAML_UID_AND_PASS_SETTING)],
            limit=1,
            context=context
        )
        if config_ids:
            config_obj.write(
                cr, uid, config_ids, {'value': setting_value}, context=context
            )
        else:
            # The setting doesn't exist; create it.
            config_obj.create(
                cr, uid,
                {'key': _SAML_UID_AND_PASS_SETTING, 'value': setting_value},
                context=context
            )
