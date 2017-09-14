# -*- coding: utf-8 -*-
# Copyright 2015 Innoviu srl <http://www.innoviu.it>
# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
#           <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import imaplib
from datetime import datetime
import time
from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):

    _inherit = "fetchmail.server"

    last_internal_date = fields.Datetime(
        'Last Download Date',
        help="Remote emails with a date greater than this will be "
             "downloaded. Only available with IMAP")

    @api.model
    def _fetch_from_date_imap(self, imap_server, count, failed):
        MailThread = self.env['mail.thread']
        messages = []
        date_uids = {}
        last_date = False
        last_internal_date = datetime.strptime(self.last_internal_date,
                                               "%Y-%m-%d %H:%M:%S")
        search_status, uids = imap_server.search(
            None,
            'SINCE', '%s' % last_internal_date.strftime('%d-%b-%Y')
            )
        new_uids = uids[0].split()
        for new_uid in new_uids:
            fetch_status, date = imap_server.fetch(
                int(new_uid),
                'INTERNALDATE'
                )
            internaldate = imaplib.Internaldate2tuple(date[0])
            internaldate_msg = datetime.fromtimestamp(
                time.mktime(internaldate)
                )
            if internaldate_msg > last_internal_date:
                messages.append(new_uid)
                date_uids[new_uid] = internaldate_msg
        for num in messages:
            # SEARCH command *always* returns at least the most
            # recent message, even if it has already been synced
            res_id = None
            result, data = imap_server.fetch(num, '(RFC822)')
            if data and data[0]:
                try:
                    res_id = MailThread.message_process(
                        self.object_id.model,
                        data[0][1],
                        save_original=self.original,
                        strip_attachments=(not self.attach))
                except Exception:
                    _logger.exception(
                        'Failed to process mail \
                        from %s server %s.',
                        self.type,
                        self.name)
                    failed += 1
                if res_id and self.action_id:
                    self.action_id.run({
                        'active_id': res_id,
                        'active_ids': [res_id],
                        'active_model': self.env.context.get(
                            "thread_model", self.object_id.model)
                    })
                imap_server.store(num, '+FLAGS', '\\Seen')
                self._cr.commit()
                count += 1
                last_date = not failed and date_uids[num] or False
        return count, failed, last_date

    @api.multi
    def fetch_mail(self):
        context = self.env.context.copy()
        context['fetchmail_cron_running'] = True
        for server in self:
            if server.type == 'imap' and server.last_internal_date:
                _logger.info(
                    'start checking for new emails, starting from %s on %s '
                    'server %s',
                    server.last_internal_date, server.type, server.name)
                context.update({'fetchmail_server_id': server.id,
                                'server_type': server.type})
                count, failed = 0, 0
                last_date = False
                imap_server = False
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    count, failed, last_date = server._fetch_from_date_imap(
                        imap_server, count, failed)
                except Exception:
                    _logger.exception(
                        "General failure when trying to fetch mail by date \
                        from %s server %s.",
                        server.type,
                        server.name
                        )
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
                if last_date:
                    _logger.info(
                        "Fetched %d email(s) on %s server %s, starting from "
                        "%s; %d succeeded, %d failed.", count,
                        server.type, server.name, last_date,
                        (count - failed), failed)
                    vals = {'last_internal_date': last_date}
                    server.write(vals)
        return super(FetchmailServer, self).fetch_mail()
