# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authentification - Generate Password module for Odoo
#    Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

# import threading
from openerp.tests.common import TransactionCase


class TestAuthGeneratePassword(TransactionCase):

    def setUp(self):
        super(TestAuthGeneratePassword, self).setUp()
        cr, uid = self.cr, self.uid
        self.imd_obj = self.registry('ir.model.data')
        self.ru_obj = self.registry('res.users')
        self.mm_obj = self.registry('mail.mail')
        self.demo_ru_id = self.imd_obj.get_object_reference(
            cr, uid, 'base',
            'user_demo')[1]
        self.extra_ru_id = self.imd_obj.get_object_reference(
            cr, uid, 'auth_generate_password',
            'extra_user')[1]

    # Test Section
    def test_01_generate_password(self):
        """[Functional Test] Test if generate password generate mails"""
        cr, uid = self.cr, self.uid
        ru_ids = [self.demo_ru_id, self.extra_ru_id]
        mm_qty_before = len(self.mm_obj.search(cr, uid, []))
#        threading.currentThread().testing = True
        self.ims_obj = self.registry('ir.mail_server')
        ims_ids = self.ims_obj.search(cr, uid, [])
        self.ims_obj.unlink(cr, uid, ims_ids)
        self.ru_obj.generate_password(cr, uid, ru_ids)
        mm_qty_after = len(self.mm_obj.search(cr, uid, []))

        self.assertEquals(
            mm_qty_before + len(ru_ids), mm_qty_after,
            "Generate password for %d user(s) must send %d email(s) !" % (
                len(ru_ids), len(ru_ids)))
