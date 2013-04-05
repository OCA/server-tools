# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#    All Rights Reserved
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

import simplejson
from lxml import etree
from openerp.osv.orm import Model, except_orm, browse_null
from openerp.tools.translate import _
from openerp.osv import fields
from openerp.addons.fetchmail.fetchmail import logger
from openerp.tools.misc import UnquoteEvalContext
from openerp.tools.safe_eval import safe_eval


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
        return super(fetchmail_server, self).__init__(pool, cr)

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
                })

            connection = this.connect()
            for folder in this.folder_ids:
                logger.info('start checking for emails in %s server %s',
                            folder.path, this.name)
                matcher = folder.get_algorithm()

                if connection.select(folder.path)[0] != 'OK':
                    logger.error(
                        'Could not open mailbox %s on %s' % (
                        folder.path, this.server))
                    connection.select()
                    continue
                result, msgids = connection.search(None, 'UNDELETED')
                if result != 'OK':
                    logger.error(
                        'Could not search mailbox %s on %s' % (
                        folder.path, this.server))
                    continue
                for msgid in msgids[0].split():
                    result, msgdata = connection.fetch(msgid, '(RFC822)')
                    if result != 'OK':
                        logger.error(
                            'Could not fetch %s in %s on %s' % (
                            msgid, folder.path, this.server))
                        continue

                    mail_message = self.pool.get('mail.message').parse_message(
                        msgdata[0][1], this.original)

                    if self.pool.get('mail.message').search(cr, uid, [
                        ('message_id', '=', mail_message['message-id'])]):
                        continue

                    found_ids = matcher.search_matches(
                        cr, uid, folder,
                        mail_message, msgdata[0][1])

                    if found_ids and (len(found_ids) == 1 or
                                      folder.match_first):
                        try:
                            matcher.handle_match(
                                cr, uid, connection,
                                found_ids[0], folder, mail_message,
                                msgdata[0][1], msgid, context)
                            cr.commit()
                        except Exception, e:
                            cr.rollback()
                            logger.exception(
                                "Failed to fetch mail %s from %s",
                                msgid, this.name)
                    elif folder.flag_nonmatching:
                        connection.store(msgid, '+FLAGS', '\\FLAGGED')
            connection.close()

        return super(fetchmail_server, self).fetch_mail(
            cr, uid, check_original, context)

    def attach_mail(
            self, cr, uid, ids, connection, object_id, folder,
            mail_message, msgid, context=None):
        for this in self.browse(cr, uid, ids, context):
            partner_id = None
            if folder.model_id.model == 'res.partner':
                partner_id = object_id
            if 'partner_id' in self.pool.get(folder.model_id.model)._columns:
                partner_id = self.pool.get(
                    folder.model_id.model).browse(
                        cr, uid, object_id, context
                    ).partner_id.id

            self.pool.get('mail.message').create(
                cr, uid,
                {
                    'partner_id': partner_id,
                    'model': folder.model_id.model,
                    'res_id': object_id,
                    'body_text': mail_message.get('body'),
                    'body_html': mail_message.get('body_html'),
                    'subject': mail_message.get('subject'),
                    'email_to': mail_message.get('to'),
                    'email_from': mail_message.get('from'),
                    'email_cc': mail_message.get('cc'),
                    'reply_to': mail_message.get('reply'),
                    'date': mail_message.get('date'),
                    'message_id': mail_message.get('message-id'),
                    'subtype': mail_message.get('subtype'),
                    'headers': mail_message.get('headers'),
                },
                context)
            if this.attach:
                # TODO: create attachments
                pass
            if folder.delete_matching:
                connection.store(msgid, '+FLAGS', '\\DELETED')

    def button_confirm_login(self, cr, uid, ids, context=None):
        retval = super(fetchmail_server, self).button_confirm_login(cr, uid,
                                                                    ids,
                                                                    context)

        for this in self.browse(cr, uid, ids, context):
            this.write({'state': 'draft'})
            connection = this.connect()
            connection.select()
            for folder in this.folder_ids:
                if connection.select(folder.path)[0] != 'OK':
                    raise except_orm(
                        _('Error'), _('Mailbox %s not found!') %
                        folder.path)
                folder.get_algorithm().search_matches(
                    cr, uid, folder, browse_null(), '')
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
