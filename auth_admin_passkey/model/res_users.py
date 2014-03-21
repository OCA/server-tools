# -*- encoding: utf-8 -*-
################################################################################
#    See __openerp__.py file for Copyright and Licence Informations.
################################################################################

import datetime
from ast import literal_eval

from openerp import SUPERUSER_ID
from openerp import pooler
from openerp import exceptions
from openerp.osv.orm import Model

class res_users(Model):
    _inherit = "res.users"

    ### Private Function section
    def _send_email_passkey(self, cr, user_id, user_agent_env):
        """ Send a email to the admin of the system to inform passkey use """
        mail_obj = self.pool.get('mail.mail')
        icp_obj = self.pool.get('ir.config_parameter')
        admin_user = self.browse(cr, SUPERUSER_ID, SUPERUSER_ID)
        login_user = self.browse(cr, SUPERUSER_ID, user_id)
        send_to_admin = literal_eval(icp_obj.get_param(cr, SUPERUSER_ID, 
                'auth_admin_passkey.send_to_admin', 'True'))
        send_to_user = literal_eval(icp_obj.get_param(cr, SUPERUSER_ID, 
                'auth_admin_passkey.send_to_user', 'True'))
        emails_to = []
        if send_to_admin and admin_user.email:
            emails_to.append(admin_user.email)
        if send_to_user and login_user.email:
            emails_to.append(login_user.email)
        if emails_to:
            body = "Admin user used his passkey to login with '%s'.\n\n" %(login_user.login)
            body += "\n\nTechnicals informations belows : \n\n"
            body += "- Login date : %s\n\n" %(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            for key, value in user_agent_env.iteritems():
                body +=("- %s : %s\n\n") % (key, value)
            for email_to in emails_to:
                mail_obj.create(cr, SUPERUSER_ID, {
                    'email_to': email_to,
                    'subject': "Passkey used",
                    'body_html': '<pre>%s</pre>' % body})

    ### Overload Section
    def authenticate(self, db, login, password, user_agent_env):
        """ Authenticate the user 'login' is password is ok 
        or if is admin password. In the second case, send mail to user and admin."""
        user_id = super(res_users, self).authenticate(db, login, password, user_agent_env)
        if user_id != SUPERUSER_ID:
            cr = pooler.get_db(db).cursor()
            try:
                # directly use parent 'check_credentials' function 
                # to really know if credentials are ok or if it was admin password
                super(res_users, self).check_credentials(cr, SUPERUSER_ID, password)
                self._send_email_passkey(cr, user_id, user_agent_env)
                cr.commit()
            except exceptions.AccessDenied:
                pass
            finally:
                cr.close()
        return user_id

    def check_credentials(self, cr, uid, password):
        """ Return now True if credentials are good OR if password is admin password"""
        try:
            super(res_users, self).check_credentials(cr, SUPERUSER_ID, password)
            return True
        except exceptions.AccessDenied:
            return super(res_users, self).check_credentials(cr, uid, password)

