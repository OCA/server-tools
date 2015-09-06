# -*- coding: utf-8 -*-
# License and authorship information in:
# __openerp__.py file at the root folder of this module.

from openerp import api, exceptions, models, SUPERUSER_ID, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    SELF_WRITEABLE_FIELDS = ['signature', 'action_id', 'company_id', 'email',
                             'name', 'image', 'image_medium', 'image_small',
                             'lang', 'tz']

    def _can_change_password(self):
        group_ok = 'base.group_erp_manager'
        user = self.env['res.users'].browse(self.env.uid)
        return user and user.has_group(group_ok) or user.id == SUPERUSER_ID

    @api.multi
    def preference_change_password(self):
        """Only allow to change passwords to users belonging to
        'Access Rights' group (or higher).
        """
        if not self._can_change_password():
            raise exceptions.AccessError(
                _("ERROR! You are not allowed to change passwords!"))
        return super(ResUsers, self).preference_change_password()

    @api.model
    def change_password(self, old_passwd, new_passwd):
        if not self._can_change_password():
            raise exceptions.AccessError(
                _("ERROR! You are not allowed to change passwords!"))
        return super(ResUsers, self).change_password(old_passwd, new_passwd)

    @api.multi
    def write(self, values):
        '''If user is trying to change password and allowed,
        remove the key from the values dictionary to avoid the change
        and even raise an exception, as this should be considered a
        security attack.
        '''
        if 'password' in values and not self._can_change_password():
            del values['password']
            raise exceptions.AccessError(
                _("ERROR! You are not allowed to change passwords!"))
        return super(ResUsers, self).write(values)
