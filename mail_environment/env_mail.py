# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
##############################################################################
from osv import fields
from osv import osv

from server_environment import serv_config


class IRMAIL(osv.osv):
    _inherit = "ir.mail_server"
    
    def _get_smtp_conf(self, cursor, uid, ids, name, args, context=None):
        """
        Return configuration
        """
        res = {}
        for conf in self.browse(cursor, uid, ids):
            res_dict = dict(serv_config.items('outgoing_mail'))
            res_dict['smtp_port'] = int(res_dict.get('smtp_port', 587))
            res[conf.id] = res_dict
        return res

    _columns = {
        'smtp_host': fields.function(_get_smtp_conf, 
                                     method=True,
                                     string='SMTP Server',
                                     type="char",
                                     multi='smtp_host',
                                     size=128),
        'smtp_port': fields.function(_get_smtp_conf,
                                     method=True,
                                     string='SMTP Port',
                                     type="integer",
                                     multi='smtp_port',
                                     help="SMTP Port. Usually 465 for SSL, and 25 or 587 for other cases.",
                                     size=5),
        'smtp_user': fields.function(_get_smtp_conf,
                                     method=True,
                                     string='Username',
                                     type="char",
                                     multi='smtp_user',
                                     help="Optional username for SMTP authentication",
                                     size=64),
        'smtp_pass': fields.function(_get_smtp_conf,
                                     method=True,
                                     string='Password',
                                     type="char",
                                     multi='smtp_pass',
                                     help="Optional password for SMTP authentication",
                                     size=64),
        'smtp_encryption' :fields.function(_get_smtp_conf,
                                           method=True,
                                           string='smtp_encryption',
                                           type="char",
                                           multi='smtp_encryption',
                                           help="Choose the connection encryption scheme:\n"
                                                 "- none: SMTP sessions are done in cleartext.\n"
                                                 "- starttls: TLS encryption is requested at start of SMTP session (Recommended)\n"
                                                 "- ssl: SMTP sessions are encrypted with SSL/TLS through a dedicated port (default: 465)",
                                            size=64)}
                                            
IRMAIL()


class FetchmailServer(osv.osv):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    def _get_incom_conf(self, cursor, uid, ids, name, args, context=None):
        """
        Return configuration
        """
        res = {}
        
        for conf in self.browse(cursor, uid, ids):
            res_dict = dict(serv_config.items('incoming_mail'))
            res_dict['port'] = int(res_dict.get('port', 993))
            res_dict['is_ssl'] = bool(int(res_dict.get('is_ssl', 0)))
            res_dict['attach'] = bool(int(res_dict.get('attach', 0)))
            res_dict['original'] = bool(int(res_dict.get('original', 0)))
            res[conf.id] = res_dict
        return res

    _columns = {
        'server': fields.function(_get_incom_conf,
                                  method=True,
                                  string='Server',
                                  type="char",
                                  multi='server',
                                  size=256, help="Hostname or IP of the mail server"),
        'port': fields.function(_get_incom_conf,
                                method=True,
                                string='Port',
                                type="integer",
                                multi='port',
                                help="Hostname or IP of the mail server"),
        'type': fields.function(_get_incom_conf,
                                method=True,
                                string='Type',
                                type="char",
                                multi='type',
                                size=64,
                                help="pop, imap, local"),
        'is_ssl': fields.function(_get_incom_conf,
                                  method=True,
                                  string='Is SSL',
                                  type="boolean",
                                  multi='is_ssl',
                                  help='Connections are encrypted with SSL/TLS through'
                                       ' a dedicated port (default: IMAPS=993, POP3S=995)'),
        'attach': fields.function(_get_incom_conf,
                                  method=True,
                                  string='Keep Attachments',
                                  type="boolean",
                                  multi='attach',
                                  help="Whether attachments should be downloaded. "
                                 "If not enabled, incoming emails will be stripped of any attachments before being processed"),
        'original': fields.function(_get_incom_conf,
                                    method=True,
                                    string='Keep Original',
                                    type="boolean",
                                    multi='attach',
                                    help="Whether a full original copy of each email should be kept for reference"
                                    "and attached to each processed message. This will usually double the size of your message database."),
        'user': fields.function(_get_incom_conf,
                                method=True,
                                string='Username',
                                type="char",
                                multi='user',
                                size=64),
        'password': fields.function(_get_incom_conf,
                                    method=True,
                                    string='password',
                                    type="char",
                                    multi='password',
                                    size=64)}
FetchmailServer()                                              
                                                       
    