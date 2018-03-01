# -*- coding: utf-8 -*-
# Copyright - 2013-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import logging

from odoo import _, api, models, fields

from .. import match_algorithm


_logger = logging.getLogger(__name__)


class FetchmailServerFolder(models.Model):
    _name = 'fetchmail.server.folder'
    _rec_name = 'path'
    _order = 'sequence'

    def _get_match_algorithms(self):
        def get_all_subclasses(cls):
            return (cls.__subclasses__() +
                    [subsub
                     for sub in cls.__subclasses__()
                     for subsub in get_all_subclasses(sub)])
        return dict([(cls.__name__, cls)
                     for cls in get_all_subclasses(
                         match_algorithm.base.Base)])

    def _get_match_algorithms_sel(self):
        algorithms = []
        for cls in self._get_match_algorithms().itervalues():
            algorithms.append((cls.__name__, cls.name))
        algorithms.sort()
        return algorithms

    sequence = fields.Integer('Sequence')
    path = fields.Char(
        'Path',
        help="The path to your mail folder. Typically would be something like "
        "'INBOX.myfolder'", required=True)
    model_id = fields.Many2one(
        'ir.model', 'Model', required=True,
        help='The model to attach emails to')
    model_field = fields.Char(
        'Field (model)',
        help='The field in your model that contains the field to match '
        'against.\n'
        'Examples:\n'
        "'email' if your model is res.partner, or "
        "'partner_id.email' if you're matching sale orders")
    model_order = fields.Char(
        'Order (model)',
        help='Field(s) to order by, this mostly useful in conjunction '
        "with 'Use 1st match'")
    match_algorithm = fields.Selection(
        _get_match_algorithms_sel,
        'Match algorithm', required=True,
        help='The algorithm used to determine which object an email matches.')
    mail_field = fields.Char(
        'Field (email)',
        help='The field in the email used for matching. Typically '
        "this is 'to' or 'from'")
    server_id = fields.Many2one('fetchmail.server', 'Server')
    delete_matching = fields.Boolean(
        'Delete matches',
        help='Delete matched emails from server')
    flag_nonmatching = fields.Boolean(
        'Flag nonmatching',
        default=True,
        help="Flag emails in the server that don't match any object in Odoo")
    match_first = fields.Boolean(
        'Use 1st match',
        help='If there are multiple matches, use the first one. If '
        'not checked, multiple matches count as no match at all')
    domain = fields.Char(
        'Domain',
        help='Fill in a search filter to narrow down objects to match')
    msg_state = fields.Selection(
        selection=[('sent', 'Sent'), ('received', 'Received')],
        string='Message state',
        default='received',
        help='The state messages fetched from this folder should be '
        'assigned in Odoo')
    active = fields.Boolean('Active', default=True)

    @api.multi
    def get_algorithm(self):
        return self._get_match_algorithms()[self.match_algorithm]()

    @api.multi
    def button_attach_mail_manually(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fetchmail.attach.mail.manually',
            'target': 'new',
            'context': dict(self.env.context, default_folder_id=self.id),
            'view_type': 'form',
            'view_mode': 'form'}

    @api.multi
    def get_msgids(self, connection):
        """Return imap ids of messages to process"""
        return connection.search(None, 'UNDELETED')

    @api.multi
    def retrieve_imap_folder(self):
        """Retrieve all mails for one IMAP folder.

        For each folder on each server we create a separate connection.
        """
        for this in self:
            server = this.server_id
            try:
                _logger.info(
                    'start checking for emails in folder %s on server %s',
                    this.path, server.name)
                imap_server = server.connect()
                if imap_server.select(this.path)[0] != 'OK':
                    _logger.error(
                        'Could not open mailbox %s on %s',
                        this.path, server.name)
                    continue
                result, msgids = this.get_msgids(imap_server)
                if result != 'OK':
                    _logger.error(
                        'Could not search mailbox %s on %s',
                        this.path, server.name)
                    continue
                match_algorithm = this.get_algorithm()
                for msgid in msgids[0].split():
                    this.apply_matching(
                        imap_server, msgid, match_algorithm)
                _logger.info(
                    'finished checking for emails in %s server %s',
                    this.path, server.name)
            except Exception:
                _logger.info(_(
                    "General failure when trying to fetch mail from"
                    " %s server %s."),
                    server.type, server.name, exc_info=True)
            finally:
                if imap_server:
                    imap_server.close()
                    imap_server.logout()

    @api.multi
    def apply_matching(self, connection, msgid, match_algorithm):
        """Return ids of objects matched"""
        self.ensure_one()
        result, msgdata = connection.fetch(msgid, '(RFC822)')
        if result != 'OK':
            _logger.error(
                'Could not fetch %s in %s on %s',
                msgid, self.path, self.server_id.server)
            return
        mail_message = self.env['mail.thread'].message_parse(
            msgdata[0][1], save_original=self.server_id.original)
        if self.env['mail.message'].search(
                [('message_id', '=', mail_message['message_id'])]):
            # Ignore mails that have been handled already
            return
        matches = match_algorithm.search_matches(
            self, mail_message, msgdata[0][1])
        if matches and (len(matches) == 1 or self.match_first):
            try:
                self.env.cr.execute('savepoint apply_matching')
                match_algorithm.handle_match(
                    connection,
                    matches[0], self, mail_message,
                    msgdata[0][1], msgid)
                self.env.cr.execute('release savepoint apply_matching')
            except Exception:
                self.env.cr.execute('rollback to savepoint apply_matching')
                _logger.exception(
                    "Failed to fetch mail %s from %s",
                    msgid, self.server_id.name)
        elif self.flag_nonmatching:
            connection.store(msgid, '+FLAGS', '\\FLAGGED')

    @api.multi
    def attach_mail(self, match_object, mail_message):
        """Attach mail to match_object."""
        self.ensure_one()
        partner = False
        model_name = self.model_id.model
        if model_name == 'res.partner':
            partner = match_object
        elif 'partner_id' in self.env[model_name]._fields:
            partner = match_object.partner_id
        attachments = []
        if self.server_id.attach and mail_message.get('attachments'):
            for attachment in mail_message['attachments']:
                # Attachment should at least have filename and data, but
                # might have some extra element(s)
                if len(attachment) < 2:
                    continue
                fname, fcontent = attachment[:2]
                if isinstance(fcontent, unicode):
                    fcontent = fcontent.encode('utf-8')
                data_attach = {
                    'name': fname,
                    'datas': base64.b64encode(str(fcontent)),
                    'datas_fname': fname,
                    'description': _('Mail attachment'),
                    'res_model': model_name,
                    'res_id': match_object.id}
                attachments.append(
                    self.env['ir.attachment'].create(data_attach))
        self.env['mail.message'].create({
            'author_id': partner and partner.id or False,
            'model': model_name,
            'res_id': match_object.id,
            'message_type': 'email',
            'body': mail_message.get('body'),
            'subject': mail_message.get('subject'),
            'email_from': mail_message.get('from'),
            'date': mail_message.get('date'),
            'message_id': mail_message.get('message_id'),
            'attachment_ids': [(6, 0, [a.id for a in attachments])]})
