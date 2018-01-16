# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock

from odoo import _
from odoo.exceptions import AccessError
from odoo.tests.common import HttpCase, TransactionCase


class TestExport(TransactionCase):
    def setUp(self):
        super(TestExport, self).setUp()
        export_group = self.env.ref('base_export_security.export_group')
        self.authorized_user = self.env['res.users'].create({
            'login': 'exporttestuser',
            'partner_id': self.env['res.partner'].create({
                'name': "Export Test User"
            }).id,
            'groups_id': [(4, export_group.id, 0)],
        })
        self.unauthorized_user = self.env['res.users'].create({
            'login': 'unauthorizedexporttestuser',
            'partner_id': self.env['res.partner'].create({
                'name': "Unauthorized Export Test User"
            }).id,
        })
        self.model_name = 'ir.module.module'
        self.recordset = self.env[self.model_name].search([])
        self.field_names = ['name', 'id']
        self.model = self.env['ir.model'].search([
            ('model', '=', self.model_name),
        ])
        self.records = self.env['ir.model.data'].search([
            ('model', '=', self.model_name),
            ('res_id', 'in', self.recordset.ids),
        ])
        self.fields = self.env['ir.model.fields'].search([
            ('model', '=', self.model_name),
            ('name', 'in', self.field_names),
        ])

    def test_log_export(self):
        """It should create a new Export record with correct data"""
        log = self.env['export.event'].sudo(self.authorized_user).log_export(
            self.recordset,
            self.field_names,
        )
        self.assertEqual(
            [log.model_id, log.field_ids, log.record_ids, log.user_id],
            [self.model, self.fields, self.records, self.authorized_user],
            'Log not created properly',
        )

    def test_log_export_posts_notification(self):
        """It should call post_notification method"""
        post_notification_mock = mock.MagicMock()
        self.env['export.event']._patch_method(
            'post_notification',
            post_notification_mock,
        )
        self.env['export.event'].sudo(self.authorized_user).log_export(
            self.recordset,
            self.field_names,
        )
        post_notification_mock.assert_called_once_with()
        self.env['export.event']._revert_method('post_notification')

    def test_post_notification(self):
        """It should post a notification with appropriate data
        to the #data export channel"""
        export = self.env['export.event'].create({
            'model_id': self.model.id,
            'field_ids': [(4, self.fields.ids)],
            'record_ids': [(4, self.records.ids)],
            'user_id': self.authorized_user.id,
        })
        message = export.sudo().post_notification()
        field_labels = ', '.join(
            self.fields.sorted().mapped('field_description'),
        )
        message_data = {
            'records': len(self.records.ids),
            'model': self.model.name,
            'user': self.authorized_user.name,
            'fields': field_labels,
        }
        message_body = _(
            '<p>%(records)d <b>%(model)s</b> records exported by <b>%(user)s'
            '</b>.<br><b>Fields exported:</b> %(fields)s</p>'
        ) % message_data
        self.assertEqual(
            [message.body, message.message_type, message.model],
            [message_body, 'notification', 'mail.channel'],
            'Message not posted properly',
        )

    def test_export_data_access(self):
        """It should raise AccessError if user does not have export rights"""
        with self.assertRaises(AccessError):
            self.env[self.model_name].sudo(
                self.unauthorized_user
            ).export_data(self, None)

    def test_export_data_calls_log_export(self):
        """It should call log_export if user has export rights"""
        log_export_mock = mock.MagicMock()
        self.env['export.event']._patch_method('log_export', log_export_mock)
        model = self.env[self.model_name]
        model.sudo(self.authorized_user).export_data(self.field_names)
        log_export_mock.assert_called_once_with(model, self.field_names)
        self.env['export.event']._revert_method('log_export')


class TestJS(HttpCase):
    def test_export_visibility(self):
        """Test visibility of export menu item"""
        self.phantom_js(
            "/web/tests?debug=assets&module=base_export_security",
            "",
            login="admin",
        )
