# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)
MAX_POP_MESSAGES = 50
MAIL_TIMEOUT = 60


class FetchmailServer(models.Model):

    _inherit = "fetchmail.server"

    default_imap_path = fields.Char(
        string="Default IMAP Path",
        help="Default IMAP path to select when fetching emails.",
        default="Odoo"
    )

    def connect(self, allow_archived=False):
        """Connect to the mail server and return the mailbox object.

        This method connects to the mail server using the server's configuration
        parameters, and returns the mailbox object. If the server is configured to
        use a default IMAP path, the mailbox is set to select this path.

        :param allow_archived: Whether to allow selecting archived emails.
        :return: The mailbox object connected to the mail server.
        """
        mailbox = super().connect(allow_archived=allow_archived)
        if self.default_imap_path:
            mailbox.select(self.default_imap_path)
        return mailbox

    def fetch_mail(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        for server in self:
            _logger.info('start checking for new emails on %s server %s', server.server_type, server.name)
            additionnal_context['default_fetchmail_server_id'] = server.id
            count, failed = 0, 0
            imap_server = None
            pop_server = None
            connection_type = server._get_connection_type()
            if connection_type == 'imap':
                try:
                    imap_server = server.connect()
                    if not server.default_imap_path:
                        imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN)')
                    for num in data[0].split():
                        res_id = None
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        try:
                            res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, data[0][1], save_original=server.original, strip_attachments=(not server.attach))
                        except Exception:
                            _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                            failed += 1
                        imap_server.store(num, '+FLAGS', '\\Seen')
                        self._cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.server_type, server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if imap_server:
                        try:
                            imap_server.close()
                            imap_server.logout()
                        except OSError:
                            _logger.warning('Failed to properly finish imap connection: %s.', server.name, exc_info=True)
            elif connection_type == 'pop':
                try:
                    while True:
                        failed_in_loop = 0
                        num = 0
                        pop_server = server.connect()
                        (num_messages, total_size) = pop_server.stat()
                        pop_server.list()
                        for num in range(1, min(MAX_POP_MESSAGES, num_messages) + 1):
                            (header, messages, octets) = pop_server.retr(num)
                            message = (b'\n').join(messages)
                            res_id = None
                            try:
                                res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, message, save_original=server.original, strip_attachments=(not server.attach))
                                pop_server.dele(num)
                            except Exception:
                                _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                                failed += 1
                                failed_in_loop += 1
                            self.env.cr.commit()
                        _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", num, server.server_type, server.name, (num - failed_in_loop), failed_in_loop)
                        # Stop if (1) no more message left or (2) all messages have failed
                        if num_messages < MAX_POP_MESSAGES or failed_in_loop == num:
                            break
                        pop_server.quit()
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if pop_server:
                        try:
                            pop_server.quit()
                        except OSError:
                            _logger.warning('Failed to properly finish pop connection: %s.', server.name, exc_info=True)
            server.write({'date': fields.Datetime.now()})
        return True


