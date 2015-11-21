# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from openerp import http
from ..controllers.main import Main


class TestDeadMansSwitchServer(TransactionCase):
    def test_dead_mans_switch_server(self):
        if 'dead.mans.switch.client' not in self.env.registry:
            return
        data = self.env['dead.mans.switch.client']._get_data()
        http._request_stack.push(self)
        Main().alive(**data)
        instance = self.env['dead.mans.switch.instance'].search([
            ('database_uuid', '=', data['database_uuid']),
        ])
        self.assertTrue(instance)
        self.assertTrue(instance.last_seen)
        self.assertEqual(instance.display_name, data['database_uuid'])
        main_partner = self.env.ref('base.main_partner')
        instance.partner_id = main_partner
        self.assertEqual(instance.display_name, main_partner.name)
        instance._onchange_partner_id()
        self.assertEqual(instance.user_id, main_partner.user_id)
        instance.button_suspended()
        self.assertEqual(instance.state, 'suspended')
        instance.button_active()
        self.assertTrue(instance.alive)
        message_count = len(instance.message_ids)
        instance.check_alive()
        self.assertEqual(len(instance.message_ids), message_count)
        instance.log_ids.unlink()
        instance.check_alive()
        self.assertEqual(len(instance.message_ids), message_count + 1)
