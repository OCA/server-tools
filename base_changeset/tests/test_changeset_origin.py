# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase

from .common import ChangesetTestCommon


class TestChangesetOrigin(ChangesetTestCommon, TransactionCase):
    """ Check that origin - old fields are stored as expected.

    'origin' fields dynamically read fields from the partner when the state
    of the change is 'draft'. Once a change becomes 'done' or 'cancel', the
    'old' field copies the value from the partner and then the 'origin' field
    displays the 'old' value.
    """

    def _setup_rules(self):
        ChangesetFieldRule = self.env["changeset.field.rule"]
        ChangesetFieldRule.search([]).unlink()
        self.field_name = self.env.ref("base.field_res_partner__name")
        ChangesetFieldRule.create(
            {"field_id": self.field_name.id, "action": "validate"}
        )

    def setUp(self):
        super().setUp()
        self._setup_rules()
        self.partner = self.env["res.partner"].create({"name": "X"})
        # Add context for this test for compatibility with other modules' tests
        self.partner = self.partner.with_context(test_record_changeset=True)

    def test_origin_value_of_change_with_apply(self):
        """ Origin field is read from the parter or 'old' - with apply

        According to the state of the change.
        """
        with Form(self.partner) as partner_form:
            partner_form.name = "Y"
        self.assertEqual(self.partner.count_pending_changesets, 1)
        changeset = self.partner.changeset_ids
        change = changeset.change_ids
        self.assertEqual(self.partner.name, "X")
        self.assertEqual(change.origin_value_char, "X")
        self.assertEqual(change.origin_value_display, "X")
        with Form(self.partner.with_context(__no_changeset=True)) as partner_form:
            partner_form.name = "A"
        self.assertEqual(change.origin_value_char, "A")
        self.assertEqual(change.origin_value_display, "A")
        change.apply()
        self.assertEqual(change.origin_value_char, "A")
        self.assertEqual(change.origin_value_display, "A")
        with Form(self.partner.with_context(__no_changeset=True)) as partner_form:
            partner_form.name = "B"
        self.assertEqual(change.origin_value_char, "A")
        self.assertEqual(change.origin_value_display, "A")
        self.assertEqual(self.partner.count_pending_changesets, 0)

    def test_origin_value_of_change_with_cancel(self):
        """ Origin field is read from the parter or 'old' - with cancel

        According to the state of the change.
        """
        with Form(self.partner) as partner_form:
            partner_form.name = "Y"
        self.assertEqual(self.partner.count_pending_changesets, 1)
        changeset = self.partner.changeset_ids
        change = changeset.change_ids
        self.assertEqual(self.partner.name, "X")
        self.assertEqual(change.origin_value_char, "X")
        self.assertEqual(change.origin_value_display, "X")
        with Form(self.partner.with_context(__no_changeset=True)) as partner_form:
            partner_form.name = "A"
        self.assertEqual(change.origin_value_char, "A")
        self.assertEqual(change.origin_value_display, "A")
        change.cancel()
        self.assertEqual(change.origin_value_char, "A")
        self.assertEqual(change.origin_value_display, "A")
        with Form(self.partner.with_context(__no_changeset=True)) as partner_form:
            partner_form.name = "B"
        self.assertEqual(change.origin_value_char, "A")
        self.assertEqual(change.origin_value_display, "A")
        self.assertEqual(self.partner.count_pending_changesets, 0)

    def test_old_field_of_change_with_apply(self):
        """ Old field is stored when the change is applied """
        with Form(self.partner) as partner_form:
            partner_form.name = "Y"
        self.assertEqual(self.partner.count_pending_changesets, 1)
        changeset = self.partner.changeset_ids
        change = changeset.change_ids
        self.assertEqual(self.partner.name, "X")
        self.assertFalse(change.old_value_char)
        with Form(self.partner.with_context(__no_changeset=True)) as partner_form:
            partner_form.name = "A"
        self.assertFalse(change.old_value_char)
        change.apply()
        self.assertEqual(change.old_value_char, "A")
        with Form(self.partner.with_context(__no_changeset=True)) as partner_form:
            partner_form.name = "B"
        self.assertEqual(change.old_value_char, "A")
        self.assertEqual(self.partner.count_pending_changesets, 0)

    def test_old_field_of_change_with_cancel(self):
        """ Old field is stored when the change is canceled """
        with Form(self.partner) as partner_form:
            partner_form.name = "Y"
        self.assertEqual(self.partner.count_pending_changesets, 1)
        changeset = self.partner.changeset_ids
        change = changeset.change_ids
        self.assertEqual(self.partner.name, "X")
        self.assertFalse(change.old_value_char)
        with Form(self.partner.with_context(__no_changeset=True)) as partner_form:
            partner_form.name = "A"
        self.assertFalse(change.old_value_char)
        change.cancel()
        self.assertEqual(change.old_value_char, "A")
        with Form(self.partner.with_context(__no_changeset=True)) as partner_form:
            partner_form.name = "B"
        self.assertEqual(change.old_value_char, "A")
        self.assertEqual(self.partner.count_pending_changesets, 0)
