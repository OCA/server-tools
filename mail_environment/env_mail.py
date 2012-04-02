# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2012 Camptocamp SA
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

from osv import fields
from osv import osv

from server_environment import serv_config


class IrMail(osv.osv):
    _inherit = "ir.mail_server"
    
    def _get_smtp_conf(self, cursor, uid, ids, name, args, context=None):
        """
        Return configuration
        """
        res = {}
        for mail_server in self.browse(cursor, uid, ids):
            global_section_name = 'outgoing_mail'

            # default vals
            config_vals = {'smtp_port': 587}
            if serv_config.has_section(global_section_name):
                config_vals.update((serv_config.items(global_section_name)))

            custom_section_name = '.'.join((global_section_name, mail_server.name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))

            if config_vals.get('smtp_port'):
                config_vals['smtp_port'] = int(config_vals['smtp_port'])

            res[mail_server.id] = config_vals
        return res

    _columns = {
        'smtp_host': fields.function(_get_smtp_conf, 
                                     method=True,
                                     string='SMTP Server',
                                     type="char",
                                     multi='outgoing_mail_config',
                                     size=128),
        'smtp_port': fields.function(_get_smtp_conf,
                                     method=True,
                                     string='SMTP Port',
                                     type="integer",
                                     multi='outgoing_mail_config',
                                     help="SMTP Port. Usually 465 for SSL, and 25 or 587 for other cases.",
                                     size=5),
        'smtp_user': fields.function(_get_smtp_conf,
                                     method=True,
                                     string='Username',
                                     type="char",
                                     multi='outgoing_mail_config',
                                     help="Optional username for SMTP authentication",
                                     size=64),
        'smtp_pass': fields.function(_get_smtp_conf,
                                     method=True,
                                     string='Password',
                                     type="char",
                                     multi='outgoing_mail_config',
                                     help="Optional password for SMTP authentication",
                                     size=64),
        'smtp_encryption' :fields.function(_get_smtp_conf,
                                           method=True,
                                           string='smtp_encryption',
                                           type="char",
                                           multi='outgoing_mail_config',
                                           help="Choose the connection encryption scheme:\n"
                                                 "- none: SMTP sessions are done in cleartext.\n"
                                                 "- starttls: TLS encryption is requested at start of SMTP session (Recommended)\n"
                                                 "- ssl: SMTP sessions are encrypted with SSL/TLS through a dedicated port (default: 465)",
                                            size=64)}
                                            
IrMail()


class FetchmailServer(osv.osv):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    def _get_incom_conf(self, cursor, uid, ids, name, args, context=None):
        """
        Return configuration
        """
        res = {}
        for fetchmail in self.browse(cursor, uid, ids):
            global_section_name = 'incoming_mail'

            key_types = {'port': int,
                         'is_ssl': lambda a: bool(int(a)),
                         'attach': lambda a: bool(int(a)),
                         'original': lambda a: bool(int(a)),}

            # default vals
            config_vals = {'port': 993,
                           'is_ssl': 0,
                           'attach': 0,
                           'original': 0}
            if serv_config.has_section(global_section_name):
                config_vals.update(serv_config.items(global_section_name))

            custom_section_name = '.'.join((global_section_name, fetchmail.name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))

            for key, to_type in key_types.iteritems():
                if config_vals.get(key):
                    config_vals[key] = to_type(config_vals[key])
            res[fetchmail.id] = config_vals
        return res

    _columns = {
        'server': fields.function(_get_incom_conf,
                                  method=True,
                                  string='Server',
                                  type="char",
                                  multi='income_mail_config',
                                  size=256, help="Hostname or IP of the mail server"),
        'port': fields.function(_get_incom_conf,
                                method=True,
                                string='Port',
                                type="integer",
                                multi='income_mail_config',
                                help="Hostname or IP of the mail server"),
        'type': fields.function(_get_incom_conf,
                                method=True,
                                string='Type',
                                type="char",
                                multi='income_mail_config',
                                size=64,
                                help="pop, imap, local"),
        'is_ssl': fields.function(_get_incom_conf,
                                  method=True,
                                  string='Is SSL',
                                  type="boolean",
                                  multi='income_mail_config',
                                  help='Connections are encrypted with SSL/TLS through'
                                       ' a dedicated port (default: IMAPS=993, POP3S=995)'),
        'attach': fields.function(_get_incom_conf,
                                  method=True,
                                  string='Keep Attachments',
                                  type="boolean",
                                  multi='income_mail_config',
                                  help="Whether attachments should be downloaded. "
                                 "If not enabled, incoming emails will be stripped of any attachments before being processed"),
        'original': fields.function(_get_incom_conf,
                                    method=True,
                                    string='Keep Original',
                                    type="boolean",
                                    multi='income_mail_config',
                                    help="Whether a full original copy of each email should be kept for reference"
                                    "and attached to each processed message. This will usually double the size of your message database."),
        'user': fields.function(_get_incom_conf,
                                method=True,
                                string='Username',
                                type="char",
                                multi='income_mail_config',
                                size=64),
        'password': fields.function(_get_incom_conf,
                                    method=True,
                                    string='password',
                                    type="char",
                                    multi='income_mail_config',
                                    size=64)}
FetchmailServer()                                              
