# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import datetime

from openerp import _, api, exceptions, models, registry, SUPERUSER_ID
from openerp.tools.safe_eval import safe_eval


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_translation(self, lang, text):
        context = {'lang': lang}  # noqa: _() checks page for locals
        return _(text)

    @api.model
    def _send_email_passkey(self, user_agent_env):
        """ Send a email to the admin of the system and / or the user
 to inform passkey use."""
        mails = []
        mail_obj = self.env['mail.mail']
        icp_obj = self.env['ir.config_parameter']
        admin_user = self.sudo().browse(SUPERUSER_ID)
        login_user = self.sudo().browse(self.env.uid)
        send_to_admin = safe_eval(icp_obj.sudo().get_param(
            'auth_admin_passkey.send_to_admin',
            'True'))
        send_to_user = safe_eval(icp_obj.sudo().get_param(
            'auth_admin_passkey.send_to_user',
            'True'))

        if send_to_admin and admin_user.email:
            mails.append({'email': admin_user.email, 'lang': admin_user.lang})
        if send_to_user and login_user.email:
            mails.append({'email': login_user.email, 'lang': login_user.lang})
        for mail in mails:
            subject = self._get_translation(
                mail['lang'], _('Passkey used'))
            body = self._get_translation(
                mail['lang'],
                _("""Admin user used his passkey to login with '%s'.\n\n"""
                    """\n\nTechnicals informations belows : \n\n"""
                    """- Login date : %s\n\n""")) % (
                        login_user.login,
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            for k, v in user_agent_env.iteritems():
                body += ("- %s : %s\n\n") % (k, v)
            mail = mail_obj.sudo().create({
                'email_to': mail['email'],
                'subject': subject,
                'body_html': '<pre>%s</pre>' % body})
            mail.send(auto_commit=True)

    @api.cr
    def _send_email_same_password(self, cr, login_user):
        """ Send a email to the admin user to inform that another user has the
 same password as him."""
        mail_obj = self.pool['mail.mail']
        admin_user = self.browse(cr, SUPERUSER_ID, SUPERUSER_ID)
        if admin_user.email:
            mail_id = mail_obj.create(cr, SUPERUSER_ID, {
                'email_to': admin_user.email,
                'subject': self._get_translation(
                    admin_user.lang, _('[WARNING] Odoo Security Risk')),
                'body_html': self._get_translation(
                    admin_user.lang, _(
                        """<pre>User with login '%s' has the same """
                        """password as you.</pre>""")) % (login_user),
            })
            mail_obj.send(cr, SUPERUSER_ID, [mail_id], auto_commit=True)

    # Overload Section
    def authenticate(self, db, login, password, user_agent_env):
        """ Authenticate the user 'login' is password is ok or if
 is admin password. In the second case, send mail to user and admin."""
        user_id = super(ResUsers, self).authenticate(
            db, login, password, user_agent_env)
        if user_id and (user_id != SUPERUSER_ID):
            same_password = False
            cr = registry(db).cursor()
            try:
                # directly use parent 'check_credentials' function
                # to really know if credentials are ok
                # or if it was admin password
                super(ResUsers, self).check_credentials(
                    cr, SUPERUSER_ID, password)
                try:
                    # Test now if the user has the same password as admin user
                    super(ResUsers, self).check_credentials(
                        cr, user_id, password)
                    same_password = True
                except exceptions.AccessDenied:
                    pass
                if not same_password:
                    self._send_email_passkey(cr, user_id, user_agent_env)
                else:
                    self._send_email_same_password(cr, login)
            except exceptions.AccessDenied:
                pass
            finally:
                cr.close()
        return user_id

    @api.model
    def check_credentials(self, password):
        """ Return now True if credentials are good OR if password is admin
password."""
        if self.env.uid != SUPERUSER_ID:
            try:
                super(ResUsers, self).check_credentials(password)
                return True
            except exceptions.AccessDenied:
                return self.sudo().check_credentials(password)
        else:
            return super(ResUsers, self).check_credentials(password)
