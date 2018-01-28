# -*- coding: utf-8 -*-
# © 2017-2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestSubscriptionAction(TransactionCase):
    def test_subscription_action(self):
        subscription = self.env['subscription.subscription'].create({
            'name': 'testsubscription',
            'doc_source': 'res.partner,%d' % (
                self.env.ref('base.main_partner').id,
            ),
            'server_action_id': self.env['ir.actions.server'].create({
                'name': 'Subscription server action',
                'model_id': self.env.ref('base.model_res_partner').id,
                'state': 'object_write',
                'use_write': 'current',
                'fields_lines': [
                    (
                        0, 0,
                        {
                            'col1':
                            self.env.ref('base.field_res_partner_name').id,
                            'type': 'value',
                            'value': 'Duplicated by subscription',
                        }
                    )
                ],
            }).id,
        })
        self.assertEqual(
            subscription.model_id.model, subscription.doc_source._name
        )
        subscription.set_process()
        subscription.model_copy()
        self.assertEqual(
            subscription.doc_lines[-1:].document_id.name,
            'Duplicated by subscription',
        )
