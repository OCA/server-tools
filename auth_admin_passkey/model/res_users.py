# -*- encoding: utf-8 -*-
##############################################################################
#
#    Admin Passkey module for Odoo
#    Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime

from openerp import SUPERUSER_ID
from openerp import pooler
from openerp import exceptions
from openerp.osv.orm import Model
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval


class res_users(Model):
    _inherit = "res.users"

    # Private Function section
    def _get_translation(self, cr, lang, text):
        context = {'lang': lang}  # noqa: _() checks page for locals
        return _(text)

    def _send_email_passkey(self, cr, user_id, user_agent_env):
        """ Send a email to the admin of the system and / or the user
 to inform passkey use."""
        mails = []
        mail_obj = self.pool['mail.mail']
        icp_obj = self.pool['ir.config_parameter']
        admin_user = self.browse(cr, SUPERUSER_ID, SUPERUSER_ID)
        login_user = self.browse(cr, SUPERUSER_ID, user_id)
        send_to_admin = safe_eval(icp_obj.get_param(
            cr, SUPERUSER_ID, 'auth_admin_passkey.send_to_admin', 'True'))
        send_to_user = safe_eval(icp_obj.get_param(
            cr, SUPERUSER_ID, 'auth_admin_passkey.send_to_user', 'True'))

        if send_to_admin and admin_user.email:
            mails.append({'email': admin_user.email, 'lang': admin_user.lang})
        if send_to_user and login_user.email:
            mails.append({'email': login_user.email, 'lang': login_user.lang})

        for mail in mails:
            subject = self._get_translation(
                cr, mail['lang'], _('Passkey used'))
            body = self._get_translation(
                cr, mail['lang'],
                _("""Admin user used his passkey to login with '%s'.\n\n"""
                    """\n\nTechnicals informations belows : \n\n"""
                    """- Login date : %s\n\n""")) % (
                        login_user.login,
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            for k, v in user_agent_env.iteritems():
                body += ("- %s : %s\n\n") % (k, v)
            mail_obj.create(
                cr, SUPERUSER_ID, {
                    'email_to': mail['email'],
                    'subject': subject,
                    'body_html': '<pre>%s</pre>' % body})

    def _send_email_same_password(self, cr, login_user):
        """ Send a email to the admin user to inform that another user has the
 same password as him."""
        mail_obj = self.pool['mail.mail']
        admin_user = self.browse(cr, SUPERUSER_ID, SUPERUSER_ID)
        if admin_user.email:
            mail_obj.create(cr, SUPERUSER_ID, {
                'email_to': admin_user.email,
                'subject': self._get_translation(
                    cr, admin_user.lang, _('[WARNING] Odoo Security Risk')),
                'body_html': self._get_translation(
                    cr, admin_user.lang, _(
                        """<pre>User with login '%s' has the same """
                        """password as you.</pre>""")) % (login_user),
            })

    # Overload Section
    def authenticate(self, db, login, password, user_agent_env):
        """ Authenticate the user 'login' is password is ok or if
 is admin password. In the second case, send mail to user and admin."""
        user_id = super(res_users, self).authenticate(
            db, login, password, user_agent_env)
        if user_id and (user_id != SUPERUSER_ID):
            same_password = False
            cr = pooler.get_db(db).cursor()
            try:
                # directly use parent 'check_credentials' function
                # to really know if credentials are ok
                # or if it was admin password
                super(res_users, self).check_credentials(
                    cr, SUPERUSER_ID, password)
                try:
                    # Test now if the user has the same password as admin user
                    super(res_users, self).check_credentials(
                        cr, user_id, password)
                    same_password = True
                except exceptions.AccessDenied:
                    pass
                if not same_password:
                    self._send_email_passkey(cr, user_id, user_agent_env)
                else:
                    self._send_email_same_password(cr, login)
                cr.commit()
            except exceptions.AccessDenied:
                pass
            finally:
                cr.close()
        return user_id

    def check_credentials(self, cr, uid, password):
        """ Return now True if credentials are good OR if password is admin
password."""
        if uid != SUPERUSER_ID:
            try:
                super(res_users, self).check_credentials(
                    cr, uid, password)
                return True
            except exceptions.AccessDenied:
                return self.check_credentials(cr, SUPERUSER_ID, password)
        else:
            return super(res_users, self).check_credentials(cr, uid, password)
