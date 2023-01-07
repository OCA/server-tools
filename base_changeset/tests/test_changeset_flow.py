# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from .common import ChangesetTestCommon


class TestChangesetFlow(ChangesetTestCommon, TransactionCase):
    """Check how changeset are generated and applied based on the rules.

    We do not really care about the types of the fields in this test
    suite, so we only use 'char' fields.  We have to ensure that the
    general changeset flows work as expected, that is:

    * create a changeset when a manual/system write is made on partner
    * create a changeset according to the changeset rules when a source model
      is specified
    * apply a changeset change writes the value on the partner
    * apply a whole changeset writes all the changes' values on the partner
    * changes in state 'cancel' or 'done' do not write on the partner
    * when all the changes are either 'cancel' or 'done', the changeset
      becomes 'done'
    """

    def _setup_rules(self):
        ChangesetFieldRule = self.env["changeset.field.rule"]
        ChangesetFieldRule.search([]).unlink()
        self.field_name = self.env.ref("base.field_res_partner__name")
        self.field_street = self.env.ref("base.field_res_partner__street")
        self.field_street2 = self.env.ref("base.field_res_partner__street2")
        ChangesetFieldRule.create({"field_id": self.field_name.id, "action": "auto"})
        ChangesetFieldRule.create(
            {"field_id": self.field_street.id, "action": "validate"}
        )
        ChangesetFieldRule.create(
            {"field_id": self.field_street2.id, "action": "never"}
        )

    def setUp(self):
        super().setUp()
        self._setup_rules()
        self.partner = self.env["res.partner"].create(
            {"name": "X", "street": "street X", "street2": "street2 X"}
        )
        # Add context for this test for compatibility with other modules' tests
        self.partner = self.partner.with_context(test_record_changeset=True)

    def test_new_changeset(self):
        """Add a new changeset on a partner

        A new changeset is created when we write on a partner
        """
        self.partner.write({"name": "Y", "street": "street Y", "street2": "street2 Y"})
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        self.assertEqual(self.partner.count_pending_changeset_changes, 1)
        self.assert_changeset(
            self.partner,
            self.env.user,
            [
                (self.field_name, "X", "Y", "done"),
                (self.field_street, "street X", "street Y", "draft"),
                (self.field_street2, "street2 X", "street2 Y", "cancel"),
            ],
        )
        self.assertEqual(self.partner.name, "Y")
        self.assertEqual(self.partner.street, "street X")
        self.assertEqual(self.partner.street2, "street2 X")

    def test_new_changeset_empty_value(self):
        """Create a changeset change that empty a value"""
        self.partner.write({"street": False})
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        self.assert_changeset(
            self.partner,
            self.env.user,
            [(self.field_street, "street X", False, "draft")],
        )

    def test_no_changeset_empty_value_both_sides(self):
        """No changeset created when both sides have an empty value"""
        # we have to ensure that even if we write '' to a False field, we won't
        # write a changeset
        self.partner.with_context(__no_changeset=True).write({"street": False})
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.partner.write({"street": ""})
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertFalse(self.partner.changeset_ids)

    def test_apply_change(self):
        """Apply a changeset change on a partner"""
        changes = [(self.field_name, "Y", "draft")]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        for change in changeset.change_ids:
            change.get_fields_changeset_changes(changeset.model, changeset.res_id)
        changeset.change_ids.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(self.partner.name, "Y")
        self.assertEqual(changeset.change_ids.state, "done")

    def test_apply_done_change(self):
        """Done changes do not apply (already applied)"""
        changes = [(self.field_name, "Y", "done")]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        with self.assertRaises(UserError):
            changeset.change_ids.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(self.partner.name, "X")
        changeset.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(self.partner.name, "X")

    def test_apply_cancel_change(self):
        """Cancel changes do not apply"""
        changes = [(self.field_name, "Y", "cancel")]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        with self.assertRaises(UserError):
            changeset.change_ids.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(self.partner.name, "X")
        changeset.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(self.partner.name, "X")

    def test_apply_empty_value(self):
        """Apply a change that empty a value"""
        changes = [(self.field_street, False, "draft")]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        for change in changeset.change_ids:
            change.get_fields_changeset_changes(changeset.model, changeset.res_id)
        changeset.change_ids.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertFalse(self.partner.street)

    def test_apply_change_loop(self):
        """Test multiple changes"""
        changes = [
            (self.field_name, "Y", "draft"),
            (self.field_street, "street Y", "draft"),
            (self.field_street2, "street2 Y", "draft"),
        ]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        for change in changeset.change_ids:
            change.get_fields_changeset_changes(changeset.model, changeset.res_id)
        changeset.change_ids.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(self.partner.name, "Y")
        self.assertEqual(self.partner.street, "street Y")
        self.assertEqual(self.partner.street2, "street2 Y")

    def test_apply(self):
        """Apply a full changeset on a partner"""
        changes = [
            (self.field_name, "Y", "draft"),
            (self.field_street, "street Y", "draft"),
            (self.field_street2, "street2 Y", "draft"),
        ]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        self.assertEqual(self.partner.count_pending_changeset_changes, 3)
        for change in changeset.change_ids:
            change.get_fields_changeset_changes(changeset.model, changeset.res_id)
        changeset.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(self.partner.count_pending_changeset_changes, 0)
        self.assertEqual(self.partner.name, "Y")
        self.assertEqual(self.partner.street, "street Y")
        self.assertEqual(self.partner.street2, "street2 Y")

    def test_changeset_state_on_done(self):
        """Check that changeset state becomes done when changes are done"""
        changes = [(self.field_name, "Y", "draft")]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        self.assertEqual(changeset.state, "draft")
        changeset.change_ids.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(changeset.state, "done")

    def test_changeset_state_on_cancel(self):
        """Check that rev. state becomes done when changes are canceled"""
        changes = [(self.field_name, "Y", "draft")]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        self.assertEqual(changeset.state, "draft")
        changeset.change_ids.cancel()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(changeset.state, "done")

    def test_changeset_state(self):
        """Check that changeset state becomes done with multiple changes"""
        changes = [
            (self.field_name, "Y", "draft"),
            (self.field_street, "street Y", "draft"),
            (self.field_street2, "street2 Y", "draft"),
        ]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        self.assertEqual(self.partner.count_pending_changeset_changes, 3)
        self.assertEqual(changeset.state, "draft")
        changeset.apply()
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 0)
        self.assertEqual(self.partner.count_pending_changeset_changes, 0)
        self.assertEqual(changeset.state, "done")

    def test_apply_changeset_with_other_pending(self):
        """Error when applying when previous pending changesets exist"""
        changes = [(self.field_name, "Y", "draft")]
        old_changeset = self._create_changeset(self.partner, changes)
        # if the date is the same, both changeset can be applied
        to_string = fields.Datetime.to_string
        old_changeset.date = to_string(datetime.now() - timedelta(days=1))
        changes = [(self.field_name, "Z", "draft")]
        changeset = self._create_changeset(self.partner, changes)
        with self.assertRaises(UserError):
            changeset.change_ids.with_context(
                require_previous_changesets_done=True
            ).apply()
        changeset.change_ids.apply()

    def test_apply_different_changesets(self):
        """Apply different changesets at once"""
        partner2 = self.env["res.partner"].create({"name": "P2"})
        changes = [
            (self.field_name, "Y", "draft"),
            (self.field_street, "street Y", "draft"),
            (self.field_street2, "street2 Y", "draft"),
        ]
        changeset = self._create_changeset(self.partner, changes)
        self.partner._compute_changeset_ids()
        self.partner._compute_count_pending_changesets()
        self.assertEqual(self.partner.count_pending_changesets, 1)
        self.assertEqual(self.partner.count_pending_changeset_changes, 3)
        for change in changeset.change_ids:
            change.get_fields_changeset_changes(changeset.model, changeset.res_id)
        changeset2 = self._create_changeset(partner2, changes)
        partner2._compute_changeset_ids()
        partner2._compute_count_pending_changesets()
        self.assertEqual(changeset.state, "draft")
        self.assertEqual(changeset2.state, "draft")
        self.assertEqual(partner2.count_pending_changesets, 1)
        self.assertEqual(partner2.count_pending_changeset_changes, 3)
        for change in changeset2.change_ids:
            change.get_fields_changeset_changes(changeset2.model, changeset2.res_id)
        (changeset + changeset2).apply()
        self.assertEqual(self.partner.name, "Y")
        self.assertEqual(self.partner.street, "street Y")
        self.assertEqual(self.partner.street2, "street2 Y")
        self.assertEqual(partner2.name, "Y")
        self.assertEqual(partner2.street, "street Y")
        self.assertEqual(partner2.street2, "street2 Y")
        self.assertEqual(changeset.state, "done")
        self.assertEqual(changeset2.state, "done")

    def test_new_changeset_source(self):
        """Source is the user who made the change"""
        self.partner.write({"street": False})
        self.partner._compute_changeset_ids()
        changeset = self.partner.changeset_ids
        self.assertEqual(changeset.source, self.env.user)

    def test_new_changeset_source_other_model(self):
        """Define source from another model"""
        company = self.env.ref("base.main_company")
        keys = {
            "force_changeset_for_partners": True,
            "__changeset_rules_source_model": "res.company",
            "__changeset_rules_source_id": company.id,
        }
        self.partner.with_context(**keys).write({"street": False})
        self.partner._compute_changeset_ids()
        changeset = self.partner.changeset_ids
        self.assertEqual(changeset.source, company)
