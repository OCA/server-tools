# -*- coding: utf-8 -*-
# © 2015-2016 Matthieu Dietrich (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import datetime
from openerp import api, fields, models
from dateutil.relativedelta import relativedelta

from openerp.addons.server_environment import serv_config

_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    cleanup_days = fields.Integer(
        compute='_get_cleanup_conf',
        string='Expiration days',
        help="Number of days before marking an e-mail as read")

    cleanup_folder = fields.Char(
        compute='_get_cleanup_conf',
        string='Expiration folder',
        help="Folder where an e-mail marked as read will be moved.")

    purge_days = fields.Integer(
        compute='_get_cleanup_conf',
        string='Deletion days',
        help="Number of days before removing an e-mail")

    @api.multi
    def _get_cleanup_conf(self):
        """
        Return configuration
        """
        for fetchmail in self:
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

            for field in ['cleanup_days', 'purge_days', 'cleanup_folder']:
                fetchmail[field] = config_vals[field]

    def _cleanup_fetchmail_server(self, server, imap_server):
        count, failed = 0, 0
        expiration_date = datetime.date.today()
        expiration_date -= relativedelta(days=server.cleanup_days)
        search_text = expiration_date.strftime('(UNSEEN BEFORE %d-%b-%Y)')
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
        purge_date = datetime.date.today()
        purge_date -= relativedelta(days=server.purge_days)
        search_text = purge_date.strftime('(BEFORE %d-%b-%Y)')
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

    @api.multi
    def fetch_mail(self):
        """ Called before the fetch, in order to clean up
             right before retrieving emails. """
        context = self.env.context.copy()
        context['fetchmail_cron_running'] = True
        for server in self:
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
        return super(FetchmailServer, self).fetch_mail()
