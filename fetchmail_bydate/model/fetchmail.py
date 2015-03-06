# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Innoviu srl (<http://www.innoviu.it>).
#    Copyright (C) 2015 Agile Business Group http://www.agilebg.com
#    @authors
#       Roberto Onnis <roberto.onnis@innoviu.com>
#       Alessio Gerace <alessio.gerace@agilebg.com>
#       Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from openerp.osv import fields, orm
from openerp.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT as DSDTF)
import logging
import imaplib
from datetime import datetime
import time
import calendar


_logger = logging.getLogger(__name__)


class FetchmailServer(orm.Model):

    _inherit = "fetchmail.server"

    _columns = {
        'last_internal_date': fields.datetime('Last Internal Date'),
    }

    def _fetch_from_data_imap(self, cr, uid,
                              server, imap_server,
                              mail_thread, action_pool,
                              count, failed,
                              context=None):
        messages = []
        date_uids = {}
        last_date = False
        last_internal_date = datetime.strptime(
            server.last_internal_date, DSDTF)
        timestamp1 = calendar.timegm(
            last_internal_date.timetuple())
        intDate = imaplib.Time2Internaldate(timestamp1)
        search_status, uids = imap_server.search(
            None,
            'SINCE',
            '%s' % intDate
            )
        new_uids = uids[0].split()
        for new_uid in new_uids:
            fetch_status, data = imap_server.fetch(
                int(new_uid),
                'INTERNALDATE'
                )
            internaldate = imaplib.Internaldate2tuple(data[0])
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
            result, data = imap_server.uid('fetch', num,
                                           '(RFC822)')
            imap_server.store(num, '-FLAGS', '\\Seen')
            try:
                res_id = mail_thread.message_process(
                    cr, uid,
                    server.object_id.model,
                    data[0][1],
                    save_original=server.original,
                    strip_attachments=(not server.attach),
                    context=context)
            except Exception:
                _logger.exception(
                    'Failed to process mail \
                    from %s server %s.',
                    server.type,
                    server.name)
                failed += 1
            if res_id and server.action_id:
                action_pool.run(cr, uid, [server.action_id.id],
                                {'active_id': res_id,
                                 'active_ids': [res_id],
                                 'active_model': context.get(
                                     "thread_model",
                                     server.object_id.model)}
                                )
            imap_server.store(num, '+FLAGS', '\\Seen')
            cr.commit()
            count += 1
            last_date = not failed and date_uids[num] or False
        return count, failed, last_date

    def _fetch_unread_imap(self, cr, uid,
                           server, imap_server,
                           mail_thread, action_pool,
                           count, failed,
                           context=None):
        result, data = imap_server.search(None, '(UNSEEN)')
        for num in data[0].split():
            res_id = None
            result, data = imap_server.fetch(num, '(RFC822)')
            imap_server.store(num, '-FLAGS', '\\Seen')
            try:
                res_id = mail_thread.message_process(
                    cr, uid, server.object_id.model,
                    data[0][1],
                    save_original=server.original,
                    strip_attachments=(not server.attach),
                    context=context)
            except Exception:
                _logger.exception(
                    'Failed to process mail \
                    from %s server %s.',
                    server.type,
                    server.name)
                failed += 1
            if res_id and server.action_id:
                action_pool.run(cr, uid,
                                [server.action_id.id],
                                {'active_id': res_id,
                                 'active_ids': [res_id],
                                 'active_model': context.get(
                                     "thread_model",
                                     server.object_id.model)}
                                )
            imap_server.store(num, '+FLAGS', '\\Seen')
            cr.commit()
            count += 1
        return count, failed

    def _fetch_unread_pop(self, cr, uid,
                          server, mail_thread,
                          failed, action_pool,
                          context=None):
        try:
            pop_server = server.connect()
            (numMsgs, totalSize) = pop_server.stat()
            pop_server.list()
            for num in range(1, numMsgs + 1):
                (header, msges, octets) = pop_server.retr(num)
                msg = '\n'.join(msges)
                res_id = None
                try:
                    res_id = mail_thread.message_process(
                        cr, uid, server.object_id.model,
                        msg,
                        save_original=server.original,
                        strip_attachments=(not server.attach),
                        context=context)
                except Exception:
                    _logger.exception(
                        'Failed to process mail \
                        from %s server %s.',
                        server.type,
                        server.name)
                    failed += 1
                if res_id and server.action_id:
                    action_pool.run(cr, uid, [server.action_id.id],
                                    {'active_id': res_id,
                                     'active_ids': [res_id],
                                     'active_model': context.get(
                                         "thread_model",
                                         server.object_id.model)}
                                    )
                pop_server.dele(num)
                cr.commit()
            _logger.info(
                "Fetched %d email(s) on %s server %s; \
                %d succeeded, %d failed.",
                numMsgs,
                server.type,
                server.name,
                (numMsgs - failed),
                failed)
        except Exception:
            _logger.exception(
                "General failure when trying to fetch \
                mail from %s server %s.",
                server.type,
                server.name)
        finally:
            if pop_server:
                pop_server.quit()

    def fetch_mail(self, cr, uid, ids, context=None):
        """WARNING: meant for cron usage only -
        will commit() after each email!
        """
        if context is None:
            context = {}
        context['fetchmail_cron_running'] = True
        mail_thread = self.pool.get('mail.thread')
        action_pool = self.pool.get('ir.actions.server')
        for server in self.browse(cr, uid, ids, context=context):
            _logger.info('start checking for new emails on %s server %s',
                         server.type, server.name)
            context.update({'fetchmail_server_id': server.id,
                            'server_type': server.type})
            count, failed = 0, 0
            last_date = False
            imap_server = False
            if server.type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    if server.last_internal_date:
                        count, failed, last_date = self._fetch_from_data_imap(
                            cr,
                            uid,
                            server,
                            imap_server,
                            mail_thread,
                            action_pool,
                            count,
                            failed,
                            context=context)
                    count, failed = self._fetch_unread_imap(
                        cr,
                        uid,
                        server,
                        imap_server,
                        mail_thread,
                        action_pool,
                        count,
                        failed,
                        context=context)
                    _logger.info(
                        "Fetched %d email(s) on %s server %s; \
                        %d succeeded, %d failed.",
                        count,
                        server.type,
                        server.name,
                        (count - failed),
                        failed)
                except Exception:
                    _logger.exception(
                        "General failure when trying to fetch mail \
                        from %s server %s.",
                        server.type,
                        server.name
                        )
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            elif server.type == 'pop':
                self._fetch_unread_pop(cr, uid,
                                       server, mail_thread,
                                       failed, action_pool,
                                       context=context)
            vals = {'date':
                    time.strftime(DSDTF)
                    }
            if last_date:
                vals['last_internal_date'] = last_date
            server.write(vals)
        return True
