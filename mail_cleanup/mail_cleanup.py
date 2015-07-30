# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
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

import logging
from openerp.osv import orm, fields
from dateutil import relativedelta
from datetime import datetime

from server_environment import serv_config

_logger = logging.getLogger(__name__)


class FetchmailServer(orm.Model):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    def _get_cleanup_conf(self, cursor, uid, ids, name, args, context=None):
        """
        Return configuration
        """
        res = {}
        for fetchmail in self.browse(cursor, uid, ids):
            global_section_name = 'incoming_mail'

            # default vals
            config_vals = {'cleanup_days': False,
                           'purge_days': False,
                           'cleanup_folder': False}
            if serv_config.has_section(global_section_name):
                config_vals.update(serv_config.items(global_section_name))

            custom_section_name = '.'.join((global_section_name,
                                            fetchmail.name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))

            # convert string values to integer
            if config_vals['cleanup_days']:
                config_vals['cleanup_days'] = int(config_vals['cleanup_days'])
            if config_vals['purge_days']:
                config_vals['purge_days'] = int(config_vals['purge_days'])
            res[fetchmail.id] = config_vals
        return res

    _columns = {
        'cleanup_days': fields.function(
            _get_cleanup_conf,
            method=True,
            string='Expiration days',
            type="integer",
            multi='outgoing_mail_config',
            help="Number of days before marking an e-mail as read"),
        'cleanup_folder': fields.function(
            _get_cleanup_conf,
            method=True,
            string='Expiration folder',
            type="char",
            multi='outgoing_mail_config',
            help="Folder where an e-mail marked as read will be moved."),
        'purge_days': fields.function(
            _get_cleanup_conf,
            method=True,
            string='Deletion days',
            type="integer",
            multi='outgoing_mail_config',
            help="Number of days before removing an e-mail"),
    }

    def _cleanup_fetchmail_server(self, server, imap_server):
        count, failed = 0, 0
        expiration_date = (datetime.now() + relativedelta.relativedelta(
            days=-(server.cleanup_days))).strftime('%d-%b-%Y')
        search_text = '(UNSEEN BEFORE %s)' % expiration_date
        imap_server.select()
        result, data = imap_server.search(None, search_text)
        for num in data[0].split():
            try:
                # Mark message as read
                imap_server.store(num, '+FLAGS', '\\Seen')
                if server.cleanup_folder:
                    # To move a message, you have to COPY
                    # then DELETE the message
                    result = imap_server.copy(num, server.cleanup_folder)
                    if result[0] == 'OK':
                        imap_server.store(num, '+FLAGS', '\\Deleted')
            except Exception:
                _logger.exception('Failed to cleanup mail from %s server %s.',
                                  server.type, server.name)
                failed += 1
            count += 1
        _logger.info("Marked %d email(s) as read on %s server %s; "
                     "%d succeeded, %d failed.", count, server.type,
                     server.name, (count - failed), failed)

    def _purge_fetchmail_server(self, server, imap_server):
        # Purging e-mails older than the purge date, if available
        count, failed = 0, 0
        purge_date = (datetime.now() + relativedelta.relativedelta(
            days=-(server.purge_days))).strftime('%d-%b-%Y')
        search_text = '(BEFORE %s)' % purge_date
        imap_server.select()
        result, data = imap_server.search(None, search_text)
        for num in data[0].split():
            try:
                # Delete message
                imap_server.store(num, '+FLAGS', '\\Deleted')
            except Exception:
                _logger.exception('Failed to remove mail from %s server %s.',
                                  server.type, server.name)
                failed += 1
            count += 1
        _logger.info("Removed %d email(s) on %s server %s; "
                     "%d succeeded, %d failed.", count, server.type,
                     server.name, (count - failed), failed)

    def fetch_mail(self, cr, uid, ids, context=None):
        """ Called before the fetch, in order to clean up
             right before retrieving emails. """
        if context is None:
            context = {}
        context['fetchmail_cron_running'] = True
        for server in self.browse(cr, uid, ids, context=context):
            _logger.info('start cleaning up emails on %s server %s',
                         server.type, server.name)
            context.update({'fetchmail_server_id': server.id,
                            'server_type': server.type})
            imap_server = False
            if server.type == 'imap':
                try:
                    imap_server = server.connect()
                    if server.cleanup_days > 0:
                        self._cleanup_fetchmail_server(server, imap_server)
                    if server.purge_days > 0:
                        self._purge_fetchmail_server(server, imap_server)
                    # Do the final cleanup: delete all messages
                    # flagged as deleted
                    imap_server.expunge()
                except Exception:
                    _logger.exception("General failure when trying to cleanup "
                                      "mail from %s server %s.",
                                      server.type, server.name)
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
        return super(FetchmailServer, self).fetch_mail(cr, uid, ids,
                                                       context=context)
