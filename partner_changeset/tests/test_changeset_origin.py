# -*- coding: utf-8 -*-
# Copyright 2015-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from .common import ChangesetMixin


class TestChangesetOrigin(ChangesetMixin, common.TransactionCase):
    """ Check that origin - old fields are stored as expected.

    'origin' fields dynamically read fields from the partner when the state
    of the change is 'draft'. Once a change becomes 'done' or 'cancel', the
    'old' field copies the value from the partner and then the 'origin' field
    displays the 'old' value.
    """

    def _setup_rules(self):
        ChangesetFieldRule = self.env['changeset.field.rule']
        ChangesetFieldRule.search([]).unlink()
        self.field_name = self.env.ref('base.field_res_partner_name')
        ChangesetFieldRule.create({
            'field_id': self.field_name.id,
            'action': 'validate',
        })

    def setUp(self):
        super(TestChangesetOrigin, self).setUp()
        self._setup_rules()
        self.partner = self.env['res.partner'].create({
            'name': 'X',
        })
        # Add context for this test for compatibility with other modules' tests
        self.partner = self.partner.with_context(test_partner_changeset=True)

    def test_origin_value_of_change_with_apply(self):
        """ Origin field is read from the parter or 'old' - with apply

        According to the state of the change.
        """
        self.partner.write({
            'name': 'Y',
        })
        changeset = self.partner.changeset_ids
        change = changeset.change_ids
        self.assertEqual(self.partner.name, 'X')
        self.assertEqual(change.origin_value_char, 'X')
        self.assertEqual(change.origin_value_display, 'X')
        self.partner.with_context(__no_changeset=True).write({'name': 'A'})
        # depends cannot trigger all fileds from partner. In real use case,
        # the user will probably be in different transaction, he will get the
        # new value of the field
        self.partner.invalidate_cache()
        self.assertEqual(change.origin_value_char, 'A')
        self.assertEqual(change.origin_value_display, 'A')
        change.apply()
        self.assertEqual(change.origin_value_char, 'A')
        self.assertEqual(change.origin_value_display, 'A')
        self.partner.with_context(__no_changeset=True).write({'name': 'B'})
        self.assertEqual(change.origin_value_char, 'A')
        self.assertEqual(change.origin_value_display, 'A')

    def test_origin_value_of_change_with_cancel(self):
        """ Origin field is read from the parter or 'old' - with cancel

        According to the state of the change.
        """
        self.partner.write({
            'name': 'Y',
        })
        changeset = self.partner.changeset_ids
        change = changeset.change_ids
        self.assertEqual(self.partner.name, 'X')
        self.assertEqual(change.origin_value_char, 'X')
        self.assertEqual(change.origin_value_display, 'X')
        self.partner.with_context(__no_changeset=True).write({'name': 'A'})
        # depends cannot trigger all fileds from partner. In real use case,
        # the user will probably be in different transaction, he will get the
        # new value of the field
        self.partner.invalidate_cache()
        self.assertEqual(change.origin_value_char, 'A')
        self.assertEqual(change.origin_value_display, 'A')
        change.cancel()
        self.assertEqual(change.origin_value_char, 'A')
        self.assertEqual(change.origin_value_display, 'A')
        self.partner.with_context(__no_changeset=True).write({'name': 'B'})
        self.assertEqual(change.origin_value_char, 'A')
        self.assertEqual(change.origin_value_display, 'A')

    def test_old_field_of_change_with_apply(self):
        """ Old field is stored when the change is applied """
        self.partner.write({
            'name': 'Y',
        })
        changeset = self.partner.changeset_ids
        change = changeset.change_ids
        self.assertEqual(self.partner.name, 'X')
        self.assertFalse(change.old_value_char)
        self.partner.with_context(__no_changeset=True).write({'name': 'A'})
        self.assertFalse(change.old_value_char)
        change.apply()
        self.assertEqual(change.old_value_char, 'A')
        self.partner.with_context(__no_changeset=True).write({'name': 'B'})
        self.assertEqual(change.old_value_char, 'A')

    def test_old_field_of_change_with_cancel(self):
        """ Old field is stored when the change is canceled """
        self.partner.write({
            'name': 'Y',
        })
        changeset = self.partner.changeset_ids
        change = changeset.change_ids
        self.assertEqual(self.partner.name, 'X')
        self.assertFalse(change.old_value_char)
        self.partner.with_context(__no_changeset=True).write({'name': 'A'})
        self.assertFalse(change.old_value_char)
        change.cancel()
        self.assertEqual(change.old_value_char, 'A')
        self.partner.with_context(__no_changeset=True).write({'name': 'B'})
        self.assertEqual(change.old_value_char, 'A')
