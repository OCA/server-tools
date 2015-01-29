# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from openerp.tests.common import TransactionCase


class TestAuditlog(TransactionCase):
    def test_LogCreation(self):
        auditlog_log = self.env['auditlog.log']
        user_model_id = self.env.ref('base.model_res_users').id
        self.env['auditlog.rule'].create({
            'name': 'testrule for users',
            'model_id': user_model_id,
            'log_create': True,
            'log_write': True,
            'log_unlink': True,
            'state': 'subscribed',
        })
        user = self.env['res.users'].create({
            'login': 'testuser',
            'name': 'testuser',
        })
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', user_model_id),
            ('method', '=', 'create'),
            ('res_id', '=', user.id),
        ]))
        user.write({'name': 'Test User'})
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', user_model_id),
            ('method', '=', 'write'),
            ('res_id', '=', user.id),
        ]))
        user.unlink()
        self.assertTrue(auditlog_log.search([
            ('model_id', '=', user_model_id),
            ('method', '=', 'unlink'),
            ('res_id', '=', user.id),
        ]))
