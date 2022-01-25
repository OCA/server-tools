# Copyright 2021 Hunki Enterprises BV (<https://hunki-enterprises.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from .common import ChangesetTestCommon


class TestChangesetFlow(ChangesetTestCommon, TransactionCase):
    """ Check that changesets don't leak information """

    def setUp(self):
        super().setUp()
        self.env['changeset.field.rule'].search([]).unlink()
        self.rule = self.env['changeset.field.rule'].create({
            'model_id': self.env.ref('base.model_ir_config_parameter').id,
            'field_id': self.env.ref('base.field_ir_config_parameter__key').id,
            'action': 'auto',
        })

    def test_change_unprivileged_user(self):
        """
        Check that unprivileged users can't see changesets they didn't create
        """
        user = self.env.ref('base.user_demo')
        self.env['ir.config_parameter'].with_context(
            test_record_changeset=True,
        ).set_param('hello', 'world')
        changeset = self.env['record.changeset.change'].search([
            ('rule_id', '=', self.rule.id),
        ])
        self.assertTrue(changeset)
        self.assertFalse(changeset.sudo(user).search([('id', '=', changeset.id)]))
