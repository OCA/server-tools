# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
from openerp.tools.translate import load_language


class TestActionMailTranslate(common.TransactionCase):

    def setUp(self):
        super(TestActionMailTranslate, self).setUp()

        self.action_model = self.registry('ir.actions.server')
        self.sequence_model = self.registry('ir.sequence')
        self.user_model = self.registry('res.users')
        self.translation_model = self.registry('ir.translation')

        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        load_language(cr, 'fr_FR')

        self.user_model.write(cr, uid, [uid], {
            'lang': 'fr_FR',
        }, context=context)

        self.action_id = self.action_model.create(cr, uid, {
            'name': 'Reminder to Responsible',
            'model_id': self.ref('base.model_ir_sequence'),
            'condition': True,
            'type': 'ir.actions.server',
            'state': 'email',
            'email': 'object.user_id.email',
            'subject': "Reminder on Action",
            'message': "Hello, This is a test",
        }, context=context)

        self.translation_model.create(cr, uid, {
            'lang': 'fr_FR',
            'module': 'ir_action_mail_translate',
            'src': "Hello, This is a test",
            'source': "Hello, This is a test",
            'type': 'model',
            'state': 'translated',
            'res_id': self.action_id,
            'name': 'ir.actions.server,message',
            'value': "Bonjour, ceci est un test",
        }, context=context)

        self.action = self.action_model.browse(
            cr, uid, self.action_id, context=context)

    def test_merge_message(self):
        cr, uid, context = self.cr, self.uid, self.context
        message = self.action_model.merge_message(
            cr, uid, self.action.message, self.action, context=context)

        self.assertEqual(message, "Bonjour, ceci est un test")
