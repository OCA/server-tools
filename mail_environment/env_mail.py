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

from openerp.osv import orm, fields

from openerp.addons.server_environment import serv_config


class IrMail(orm.Model):
    _inherit = "ir.mail_server"

    def _get_smtp_conf(self, cr, uid, ids, name, args, context=None):
        """
        Return configuration
        """
        res = {}
        for mail_server in self.browse(cr, uid, ids, context=context):
            global_section_name = 'outgoing_mail'

            # default vals
            config_vals = {'smtp_port': 587}
            if serv_config.has_section(global_section_name):
                config_vals.update((serv_config.items(global_section_name)))

            custom_section_name = '.'.join((global_section_name,
                                            mail_server.name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))

            if config_vals.get('smtp_port'):
                config_vals['smtp_port'] = int(config_vals['smtp_port'])

            res[mail_server.id] = config_vals
        return res

    _columns = {
        'smtp_host': fields.function(
            _get_smtp_conf,
            string='SMTP Server',
            type="char",
            multi='outgoing_mail_config',
            states={'draft': [('readonly', True)]},
            help="Hostname or IP of SMTP server"),
        'smtp_port': fields.function(
            _get_smtp_conf,
            string='SMTP Port',
            type="integer",
            multi='outgoing_mail_config',
            states={'draft': [('readonly', True)]},
            help="SMTP Port. Usually 465 for SSL, "
                 "and 25 or 587 for other cases.",
            size=5),
        'smtp_user': fields.function(
            _get_smtp_conf,
            string='Username',
            type="char",
            multi='outgoing_mail_config',
            states={'draft': [('readonly', True)]},
            help="Optional username for SMTP authentication",
            size=64),
        'smtp_pass': fields.function(
            _get_smtp_conf,
            string='Password',
            type="char",
            multi='outgoing_mail_config',
            states={'draft': [('readonly', True)]},
            help="Optional password for SMTP authentication",
            size=64),
        'smtp_encryption': fields.function(
            _get_smtp_conf,
            string='smtp_encryption',
            type="selection",
            multi='outgoing_mail_config',
            selection=[('none', 'None'),
                       ('starttls', 'TLS (STARTTLS)'),
                       ('ssl', 'SSL/TLS')],
            states={'draft': [('readonly', True)]},
            help="Choose the connection encryption scheme:\n"
                 "- none: SMTP sessions are done in cleartext.\n"
                 "- starttls: TLS encryption is requested at start "
                 "of SMTP session (Recommended)\n"
                 "- ssl: SMTP sessions are encrypted with SSL/TLS "
                 "through a dedicated port (default: 465)")
    }


class FetchmailServer(orm.Model):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    def _get_incom_conf(self, cr, uid, ids, name, args, context=None):
        """
        Return configuration
        """
        res = {}
        for fetchmail in self.browse(cr, uid, ids, context=context):
            global_section_name = 'incoming_mail'

            key_types = {'port': int,
                         'is_ssl': lambda a: bool(int(a)),
                         'attach': lambda a: bool(int(a)),
                         'original': lambda a: bool(int(a)),
                         }

            # default vals
            config_vals = {'port': 993,
                           'is_ssl': 0,
                           'attach': 0,
                           'original': 0,
                           }
            if serv_config.has_section(global_section_name):
                config_vals.update(serv_config.items(global_section_name))

            custom_section_name = '.'.join((global_section_name,
                                            fetchmail.name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))

            for key, to_type in key_types.iteritems():
                if config_vals.get(key):
                    config_vals[key] = to_type(config_vals[key])
            res[fetchmail.id] = config_vals
        return res

    def _type_search(self, cr, uid, obj, name, args, context=None):
        result_ids = []
        # read all incoming servers values
        all_ids = self.search(cr, uid, [], context=context)
        results = self.read(cr, uid, all_ids, ['id', 'type'], context=context)
        args = args[:]
        i = 0
        while i < len(args):
            operator = args[i][1]
            if operator == '=':
                for res in results:
                    if (res['type'] == args[i][2] and
                            res['id'] not in result_ids):
                        result_ids.append(res['id'])
            elif operator == 'in':
                for search_vals in args[i][2]:
                    for res in results:
                        if (res['type'] == search_vals and
                                res['id'] not in result_ids):
                            result_ids.append(res['id'])
            else:
                continue
            i += 1
        return [('id', 'in', result_ids)]

    _columns = {
        'server': fields.function(
            _get_incom_conf,
            string='Server',
            type="char",
            multi='income_mail_config',
            states={'draft': [('readonly', True)]},
            help="Hostname or IP of the mail server"),
        'port': fields.function(
            _get_incom_conf,
            string='Port',
            type="integer",
            states={'draft': [('readonly', True)]},
            multi='income_mail_config'),
        'type': fields.function(
            _get_incom_conf,
            string='Type',
            type="selection",
            selection=[('pop', 'POP Server'),
                       ('imap', 'IMAP Server'),
                       ('local', 'Local Server'),
                       ],
            multi='income_mail_config',
            fnct_search=_type_search,
            states={'draft': [('readonly', True)]},
            help="pop, imap, local"),
        'is_ssl': fields.function(
            _get_incom_conf,
            string='Is SSL',
            type="boolean",
            multi='income_mail_config',
            states={'draft': [('readonly', True)]},
            help='Connections are encrypted with SSL/TLS through'
                 ' a dedicated port (default: IMAPS=993, POP3S=995)'),
        'attach': fields.function(
            _get_incom_conf,
            string='Keep Attachments',
            type="boolean",
            multi='income_mail_config',
            states={'draft': [('readonly', True)]},
            help="Whether attachments should be downloaded. "
                 "If not enabled, incoming emails will be stripped of any "
                 "attachments before being processed"),
        'original': fields.function(
            _get_incom_conf,
            string='Keep Original',
            type="boolean",
            multi='income_mail_config',
            states={'draft': [('readonly', True)]},
            help="Whether a full original copy of each email should be kept "
                 "for reference and attached to each processed message. This "
                 "will usually double the size of your message database."),
        'user': fields.function(
            _get_incom_conf,
            string='Username',
            type="char",
            states={'draft': [('readonly', True)]},
            multi='income_mail_config'),
        'password': fields.function(
            _get_incom_conf,
            string='password',
            type="char",
            states={'draft': [('readonly', True)]},
            multi='income_mail_config')
    }
