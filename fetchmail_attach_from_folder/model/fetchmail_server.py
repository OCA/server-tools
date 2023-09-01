# -*- coding: utf-8 -*-
# Copyright 2013-2023 Therp BV - <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=invalid-name,missing-docstring,too-many-arguments
# pylint: disable=super-with-arguments,import-error,protected-access
# pylint: disable=too-many-locals
import base64
import email
import logging
import simplejson
from lxml import etree

from openerp.osv.orm import Model, except_orm
from openerp.tools.translate import _
from openerp.osv import fields
from openerp.tools.misc import UnquoteEvalContext

_logger = logging.getLogger(__name__)


def get_message_id(message):
    """Utility function to quickly retrieve message-id without full parse.

    The code is actually derived from parse_message in mail.message model.
    """
    msg_txt = message
    if isinstance(message, str):
        msg_txt = email.message_from_string(message)

    # Warning: message_from_string doesn't always work correctly on unicode,
    # we must use utf-8 strings here :-(

    # pylint: disable=undefined-variable
    # For some reason unicode seen as variable
    if isinstance(message, unicode):
        message = message.encode('utf-8')
        msg_txt = email.message_from_string(message)

    message_id = msg_txt.get('message-id', False)
    return message_id


class fetchmail_server(Model):
    _inherit = 'fetchmail.server'

    _columns = {
        'folder_ids': fields.one2many(
            'fetchmail.server.folder', 'server_id', 'Folders'),
    }
    _defaults = {
        'type': 'imap',
    }

    def __init__(self, pool, cr):
        self._columns['object_id'].required = False
        super(fetchmail_server, self).__init__(pool, cr)

    def onchange_server_type(
            self, cr, uid, ids, server_type=False, ssl=False,
            object_id=False):
        retval = super(
            fetchmail_server, self).onchange_server_type(cr, uid,
                                                         ids, server_type, ssl,
                                                         object_id)
        retval['value']['state'] = 'draft'
        return retval

    def fetch_mail(self, cr, uid, ids, context=None):
        """Fetch mail from folders in incoming mail servers."""
        if context is None:
            context = {}
        check_original = []
        for this in self.browse(cr, uid, ids, context):
            if this.object_id:
                check_original.append(this.id)
            context.update(
                {
                    'fetchmail_server_id': this.id,
                    'server_type': this.type
                }
            )
            connection = this.connect()
            for folder in this.folder_ids:
                this.handle_folder(connection, folder)
            connection.close()
        return super(fetchmail_server, self).fetch_mail(
            cr, uid, check_original, context)

    def handle_folder(self, cr, uid, ids, connection, folder, context=None):
        """Return ids of objects matched"""
        for this in self.browse(cr, uid, ids, context=context):
            _logger.info(
                "start checking for emails in %s server %s",
                folder.path,
                this.name
            )
            match_algorithm = folder.get_algorithm()
            if connection.select(folder.path)[0] != "OK":
                _logger.error(
                    "Could not open mailbox %s on %s",
                    folder.path,
                    this.server
                )
                connection.select()
                continue
            result, msgids = connection.search(None, "UNDELETED")
            if result != "OK":
                _logger.error(
                    "Could not search mailbox %s on %s",
                    folder.path,
                    this.server
                )
                continue
            for msgid in msgids[0].split():
                # We will accept exceptions for single messages
                try:
                    cr.execute('savepoint apply_matching')
                    rollback_org = cr.rollback
                    cr.rollback = lambda: None
                    # OpenERP 6.1 does a rollback on validation errors
                    this.apply_matching(connection, folder, msgid, match_algorithm)
                    cr.execute('release savepoint apply_matching')
                    cr.rollback = rollback_org
                except Exception:  # pylint: disable=broad-except
                    cr.rollback = rollback_org
                    cr.execute('rollback to savepoint apply_matching')
                    _logger.exception(
                        "Failed to fetch mail %s from %s",
                        msgid,
                        this.name
                    )
            _logger.info(
                'finished checking for emails in %s server %s',
                folder.path,
                this.name
            )

    def apply_matching(
            self, cr, uid, ids,
            connection, folder, msgid, match_algorithm, context=None):
        """Match retrieved mail with one or only record, else flag message."""
        message_model = self.pool["mail.message"]
        for this in self.browse(cr, uid, ids, context=context):
            # Fetch the complete message from the server.
            result, msgdata = connection.fetch(msgid, "(RFC822)")
            if result != "OK":
                _logger.error(
                    "Could not fetch %s in %s on %s",
                    msgid,
                    folder.path,
                    this.server
                )
                continue

            # Get raw message from message data.
            raw_message = msgdata[0][1]

            # Get message-id, also to prevent generation of random one
            message_id = get_message_id(raw_message)

            # Ignore mails that have been handled already
            if message_id:
                if message_model.search_count(
                    cr, uid, [("message_id", "=", message_id)]
                ):
                    continue

            # Parse message.
            mail_message = message_model.parse_message(raw_message, this.original)

            # Ignore messages without id, otherwise we would retrieve
            # those again and again, until deleted on server.
            if not message_id:
                subject = mail_message.get("subject", "No subject")
                _logger.error(
                    "Message %s in %s on %s, with subject %s, had no message-id",
                    msgid,
                    folder.path,
                    this.server,
                    subject
                )
                continue

            found_ids = match_algorithm.search_matches(
                cr,
                uid,
                folder,
                mail_message,
                raw_message
            )
            if found_ids and (len(found_ids) == 1 or folder.match_first):
                match_algorithm.handle_match(
                    cr,
                    uid,
                    connection,
                    found_ids[0],
                    folder,
                    mail_message,
                    raw_message,
                    msgid,
                    context=context
                )
            elif folder.flag_nonmatching:
                connection.store(msgid, "+FLAGS", "\\FLAGGED")

    def attach_mail(
            self, cr, uid, ids, connection, object_id, folder,
            mail_message, msgid, context=None):
        """Return ids of messages created"""

        mail_message_ids = []

        for this in self.browse(cr, uid, ids, context):
            partner_id = None
            if folder.model_id.model == 'res.partner':
                partner_id = object_id
            if 'partner_id' in self.pool.get(folder.model_id.model)._columns:
                partner_id = self.pool.get(
                    folder.model_id.model).browse(
                        cr, uid, object_id, context
                ).partner_id.id

            attachments = []
            if this.attach and mail_message.get('attachments'):
                for attachment in mail_message['attachments']:
                    fname, fcontent = attachment
                    # pylint: disable=undefined-variable
                    if isinstance(fcontent, unicode):
                        fcontent = fcontent.encode('utf-8')
                    data_attach = {
                        'name': fname,
                        'datas': base64.b64encode(str(fcontent)),
                        'datas_fname': fname,
                        'description': _('Mail attachment'),
                        'res_model': folder.model_id.model,
                        'res_id': object_id,
                    }
                    attachments.append(
                        self.pool.get('ir.attachment').create(
                            cr, uid, data_attach, context=context))

            mail_message_ids.append(
                self.pool.get('mail.message').create(
                    cr, uid,
                    {
                        'partner_id': partner_id,
                        'model': folder.model_id.model,
                        'res_id': object_id,
                        'body_text': mail_message.get('body'),
                        'body_html': mail_message.get('body_html'),
                        'subject': mail_message.get('subject') or '',
                        'email_to': mail_message.get('to'),
                        'email_from': mail_message.get('from'),
                        'email_cc': mail_message.get('cc'),
                        'reply_to': mail_message.get('reply'),
                        'date': mail_message.get('date'),
                        'message_id': mail_message.get('message-id'),
                        'subtype': mail_message.get('subtype'),
                        'headers': mail_message.get('headers'),
                        'state': folder.msg_state,
                        'attachment_ids': [(6, 0, attachments)],
                    },
                    context))

            if folder.delete_matching:
                connection.store(msgid, '+FLAGS', '\\DELETED')
        return mail_message_ids

    def button_confirm_login(self, cr, uid, ids, context=None):
        retval = super(fetchmail_server, self).button_confirm_login(
            cr, uid, ids, context=context
        )
        for this in self.browse(cr, uid, ids, context):
            this.write({'state': 'draft'})
            connection = this.connect()
            connection.select()
            for folder in this.folder_ids:
                if connection.select(folder.path)[0] != 'OK':
                    raise except_orm(
                        _('Error'), _('Mailbox %s not found!') %
                        folder.path)
            connection.close()
            this.write({'state': 'done'})

        return retval

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        result = super(fetchmail_server, self).fields_view_get(
            cr, user, view_id, view_type, context, toolbar, submenu)

        if view_type == 'form':
            view = etree.fromstring(
                result['fields']['folder_ids']['views']['form']['arch'])
            modifiers = {}
            docstr = ''
            for algorithm in self.pool.get('fetchmail.server.folder')\
                    ._get_match_algorithms().itervalues():
                for modifier in ['required', 'readonly']:
                    for field in getattr(algorithm, modifier + '_fields'):
                        modifiers.setdefault(field, {})
                        modifiers[field].setdefault(modifier, [])
                        if modifiers[field][modifier]:
                            modifiers[field][modifier].insert(0, '|')
                        modifiers[field][modifier].append(
                            ("match_algorithm", "==", algorithm.__name__))
                docstr += _(algorithm.name) + '\n' + _(algorithm.__doc__) + \
                    '\n\n'

            for field in view:
                if field.tag == 'field' and field.get('name') in modifiers:
                    field.set('modifiers', simplejson.dumps(
                        dict(
                            eval(field.attrib['modifiers'],
                                 UnquoteEvalContext({})),
                            **modifiers[field.attrib['name']])))
                if (field.tag == 'field' and
                        field.get('name') == 'match_algorithm'):
                    field.set('help', docstr)
            result['fields']['folder_ids']['views']['form']['arch'] = \
                etree.tostring(view)

        return result
