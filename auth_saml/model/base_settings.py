# -*- coding: utf-8 -*-

from openerp import fields
from openerp import models
from openerp import api


_SAML_UID_AND_PASS_SETTING = 'auth_saml.allow_saml.uid_and_internal_password'


class BaseSettings(models.TransientModel):
    """Inherit from base.config.settings to add a setting. This is only here
    for easier access; the setting is not actually stored by this (transient)
    collection. Instead, it is kept in sync with the
    "auth_saml.allow_saml.uid_and_internal_password" global setting. See
    comments in the definition of the "res.config.settings" collection for
    details.
    """

    _inherit = 'base.config.settings'

    allow_saml_uid_and_internal_password = fields.Boolean(
        (
            'Allow SAML users to posess an Odoo password (warning: '
            'decreases security)'
        ),
    )

    # take care to name the function with another name to not clash with column
    @api.model
    def allow_saml_and_password(self):
        """Read the allow_saml_uid_and_internal_password setting.
        Use the admin account to bypass security restrictions.
        """

        config_obj = self.env['ir.config_parameter']
        config_objs = config_obj.sudo().search(
            [('key', '=', _SAML_UID_AND_PASS_SETTING)],
            limit=1,
        )

        # no configuration found reply with default value
        if len(config_objs) == 0:
            return False

        return (True if config_objs.value == '1' else False)

    @api.multi
    def get_default_allow_saml_uid_and_internal_password(self, fields):
        """Read the allow_saml_uid_and_internal_password setting. This function
        is called when the form is shown.
        """

        ret = {}

        if 'allow_saml_uid_and_internal_password' in fields:
            ret['allow_saml_uid_and_internal_password'] = (
                self.allow_saml_uid_and_internal_password()
            )

        return ret

    @api.multi
    def set_allow_saml_uid_and_internal_password(self):
        """Update the allow_saml_uid_and_internal_password setting. This
        function is called when saving the form.
        """

        setting_value = (
            '1' if self.allow_saml_uid_and_internal_password else '0'
        )

        config_obj = self.env['ir.config_parameter']
        config_ids = config_obj.search(
            [('key', '=', _SAML_UID_AND_PASS_SETTING)],
            limit=1,
        )

        if config_ids:
            config_ids.write({'value': setting_value})

        else:
            # The setting doesn't exist; create it.
            config_obj.create(
                {'key': _SAML_UID_AND_PASS_SETTING, 'value': setting_value},
            )
