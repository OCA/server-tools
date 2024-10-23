# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from ..models.base import disable_changeset
from .common import ChangesetTestCommon


class TestChangesetFieldType(ChangesetTestCommon, TransactionCase):
    """Check that changeset changes are stored expectingly to their types"""

    @mute_logger("odoo.models.unlink")
    def _setup_rules(self):
        ChangesetFieldRule = self.env["changeset.field.rule"]
        ChangesetFieldRule.search([]).unlink()
        fields = (
            ("char", "ref"),
            ("text", "comment"),
            ("boolean", "is_company"),
            ("date", "date"),
            ("integer", "color"),
            ("float", "credit_limit"),
            ("selection", "type"),
            ("many2one", "country_id"),
            ("many2many", "category_id"),
            ("one2many", "user_ids"),
            ("binary", "image_1920"),
        )
        for field_type, field in fields:
            attr_name = "field_%s" % field_type
            field_record = self.env["ir.model.fields"].search(
                [("model", "=", "res.partner"), ("name", "=", field)]
            )
            self.assertTrue(field_record, "Field %s not available" % field)
            # set attribute such as 'self.field_char' is a
            # ir.model.fields record of the field res_partner.ref
            setattr(self, attr_name, field_record)
            ChangesetFieldRule.create(
                {"field_id": field_record.id, "action": "validate"}
            )

    def setUp(self):
        super().setUp()
        self._setup_rules()
        self.partner = self.env["res.partner"].create(
            {"name": "Original Name", "street": "Original Street"}
        )
        # Add context for this test for compatibility with other modules' tests
        self.partner = self.partner.with_context(test_record_changeset=True)

    def test_new_changeset_char(self):
        """Add a new changeset on a Char field"""
        self.partner.write({self.field_char.name: "New value"})
        self.assert_changeset(
            self.partner,
            self.env.user,
            [
                (
                    self.field_char,
                    self.partner[self.field_char.name],
                    "New value",
                    "draft",
                )
            ],
        )

    def test_new_changeset_text(self):
        """Add a new changeset on a Text field"""
        self.partner.write({self.field_text.name: "New comment\non 2 lines"})
        self.assert_changeset(
            self.partner,
            self.env.user,
            [
                (
                    self.field_text,
                    self.partner[self.field_text.name],
                    "New comment\non 2 lines",
                    "draft",
                )
            ],
        )

    def test_new_changeset_boolean(self):
        """Add a new changeset on a Boolean field"""
        # ensure the changeset has to change the value
        self.partner.with_context(__no_changeset=disable_changeset).write(
            {self.field_boolean.name: False}
        )

        self.partner.write({self.field_boolean.name: True})
        self.assert_changeset(
            self.partner,
            self.env.user,
            [
                (
                    self.field_boolean,
                    self.partner[self.field_boolean.name],
                    True,
                    "draft",
                )
            ],
        )

    def test_new_changeset_date(self):
        """Add a new changeset on a Date field"""
        self.partner.write({self.field_date.name: "2015-09-15"})
        self.assert_changeset(
            self.partner,
            self.env.user,
            [
                (
                    self.field_date,
                    self.partner[self.field_date.name],
                    fields.Date.from_string("2015-09-15"),
                    "draft",
                )
            ],
        )

    def test_new_changeset_integer(self):
        """Add a new changeset on a Integer field"""
        self.partner.write({self.field_integer.name: 42})
        self.assert_changeset(
            self.partner,
            self.env.user,
            [(self.field_integer, self.partner[self.field_integer.name], 42, "draft")],
        )

    def test_new_changeset_float(self):
        """Add a new changeset on a Float field"""
        self.partner.write({self.field_float.name: 3.1415})
        self.assert_changeset(
            self.partner,
            self.env.user,
            [(self.field_float, self.partner[self.field_float.name], 3.1415, "draft")],
        )

    def test_new_changeset_selection(self):
        """Add a new changeset on a Selection field"""
        self.partner.write({self.field_selection.name: "delivery"})
        self.assert_changeset(
            self.partner,
            self.env.user,
            [
                (
                    self.field_selection,
                    self.partner[self.field_selection.name],
                    "delivery",
                    "draft",
                )
            ],
        )

    def test_new_changeset_many2one(self):
        """Add a new changeset on a Many2one field"""
        self.partner.with_context(__no_changeset=disable_changeset).write(
            {self.field_many2one.name: self.env.ref("base.fr").id}
        )
        self.partner.write({self.field_many2one.name: self.env.ref("base.ch").id})
        self.assert_changeset(
            self.partner,
            self.env.user,
            [
                (
                    self.field_many2one,
                    self.partner[self.field_many2one.name],
                    self.env.ref("base.ch"),
                    "draft",
                )
            ],
        )

    def test_new_changeset_many2many(self):
        """Add a new changeset on a Many2many field is not supported"""
        with self.assertRaises(NotImplementedError):
            self.partner.write(
                {self.field_many2many.name: [self.env.ref("base.ch").id]}
            )

    @mute_logger("odoo.models.unlink")
    def test_new_changeset_one2many(self):
        """Add a new changeset on a One2many field"""
        # Update one2many rule to get only login field changes
        login_field = self.env["ir.model.fields"]
        child_fields = self.env["ir.model.fields"].search(
            [
                ("model_id.model", "=", self.field_one2many.relation),
                ("name", "=", "login"),
            ]
        )
        rule = self.env["changeset.field.rule"].search(
            [("field_id.ttype", "=", "one2many")]
        )
        rule.write({"subfield_ids": child_fields.ids})
        one2many_value = [0, 0, {"login": "new-user"}]
        self.partner.write({self.field_one2many.name: [one2many_value]})
        self.partner._compute_child_changeset_ids()
        changeset = self.partner.child_changeset_ids
        self.assertEqual(changeset.action, "create")
        self.assertTrue(changeset.rule_id)
        self.assertEqual(changeset.model, self.field_one2many.relation)
        self.assertFalse(changeset.res_id)
        self.assertEqual(
            changeset.raw_changes, str({self.field_one2many.name: [one2many_value]})
        )
        self.assertTrue(changeset.raw_changes_html)
        self.assertFalse(changeset.change_ids)
        self.assertFalse(self.partner[self.field_one2many.name])
        changeset.apply()
        self.assertTrue(self.partner[self.field_one2many.name])
        self.assertEqual(changeset.state, "done")
        self.assertTrue(changeset.res_id)
        new_user_id = changeset.res_id
        changeset.unlink()
        # Update + cancel
        one2many_value = [1, new_user_id, {"login": "new-user2"}]
        self.partner.write({self.field_one2many.name: [one2many_value]})
        self.partner._compute_child_changeset_ids()
        changeset = self.partner.child_changeset_ids
        self.assertEqual(changeset.action, "write")
        self.assertEqual(changeset.model, self.field_one2many.relation)
        self.assertEqual(changeset.res_id, new_user_id)
        self.assertEqual(
            changeset.raw_changes, str({self.field_one2many.name: [one2many_value]})
        )
        login_field = self.env["ir.model.fields"].search(
            [("model_id.model", "=", "res.users"), ("name", "=", "login")]
        )
        self.assert_child_changeset(
            self.partner,
            self.env.user,
            [
                (
                    login_field,
                    "new-user",
                    "new-user2",
                    "draft",
                )
            ],
        )
        changeset.cancel()
        self.assertTrue(self.partner[self.field_one2many.name])
        self.assertEqual(changeset.state, "done")
        changeset.unlink()
        # Remove user + apply
        one2many_value = [2, new_user_id, False]
        self.partner.write({self.field_one2many.name: [one2many_value]})
        self.partner._compute_child_changeset_ids()
        changeset = self.partner.child_changeset_ids
        self.assertEqual(changeset.action, "unlink")
        self.assertEqual(changeset.model, self.field_one2many.relation)
        self.assertEqual(changeset.res_id, new_user_id)
        self.assertEqual(
            changeset.raw_changes, str({self.field_one2many.name: [one2many_value]})
        )
        self.assertFalse(changeset.change_ids)
        changeset.apply()
        self.assertFalse(self.partner[self.field_one2many.name])
        self.assertEqual(changeset.state, "done")

    def test_new_changeset_binary(self):
        """Add a new changeset on a Binary field is not supported"""
        with self.assertRaises(NotImplementedError):
            self.partner.write({self.field_binary.name: "xyz"})

    def test_apply_char(self):
        """Apply a change on a Char field"""
        changes = [(self.field_char, "New Ref", "draft")]
        changeset = self._create_changeset(self.partner, changes)
        changeset.change_ids.apply()
        self.assertEqual(self.partner[self.field_char.name], "New Ref")

    def test_apply_text(self):
        """Apply a change on a Text field"""
        changes = [(self.field_text, "New comment\non 2 lines", "draft")]
        changeset = self._create_changeset(self.partner, changes)
        changeset.change_ids.apply()
        self.assertEqual(self.partner[self.field_text.name], "New comment\non 2 lines")

    def test_apply_boolean(self):
        """Apply a change on a Boolean field"""
        # ensure the changeset has to change the value
        self.partner.write({self.field_boolean.name: False})

        changes = [(self.field_boolean, True, "draft")]
        changeset = self._create_changeset(self.partner, changes)
        changeset.change_ids.apply()
        self.assertEqual(self.partner[self.field_boolean.name], True)

        # Cannot do this while it is on the same transaction. The cache may not
        # be updated
        # changes = [(self.field_boolean, False, 'draft')]
        # changeset = self._create_changeset(self.partner, changes)
        # changeset.change_ids.apply()
        # self.assertEqual(self.partner[self.field_boolean.name], False)

    def test_apply_date(self):
        """Apply a change on a Date field"""
        changes = [(self.field_date, "2015-09-15", "draft")]
        changeset = self._create_changeset(self.partner, changes)
        changeset.change_ids.apply()
        self.assertAlmostEqual(
            self.partner[self.field_date.name], fields.Date.from_string("2015-09-15")
        )

    def test_apply_integer(self):
        """Apply a change on a Integer field"""
        changes = [(self.field_integer, 42, "draft")]
        changeset = self._create_changeset(self.partner, changes)
        changeset.change_ids.apply()
        self.assertAlmostEqual(self.partner[self.field_integer.name], 42)

    def test_apply_float(self):
        """Apply a change on a Float field"""
        changes = [(self.field_float, 52.47, "draft")]
        changeset = self._create_changeset(self.partner, changes)
        changeset.change_ids.apply()
        self.assertAlmostEqual(self.partner[self.field_float.name], 52.47)

    def test_apply_selection(self):
        """Apply a change on a Selection field"""
        changes = [(self.field_selection, "delivery", "draft")]
        changeset = self._create_changeset(self.partner, changes)
        changeset.change_ids.apply()
        self.assertAlmostEqual(self.partner[self.field_selection.name], "delivery")

    def test_apply_many2one(self):
        """Apply a change on a Many2one field"""
        self.partner.with_context(__no_changeset=disable_changeset).write(
            {self.field_many2one.name: self.env.ref("base.fr").id}
        )
        changes = [
            (
                self.field_many2one,
                "res.country,%d" % self.env.ref("base.ch").id,
                "draft",
            )
        ]
        changeset = self._create_changeset(self.partner, changes)
        changeset.change_ids.apply()
        self.assertEqual(
            self.partner[self.field_many2one.name], self.env.ref("base.ch")
        )

    def test_apply_many2many(self):
        """Apply a change on a Many2many field is not supported"""
        changes = [(self.field_many2many, self.env.ref("base.ch").id, "draft")]
        with self.assertRaises(NotImplementedError):
            self._create_changeset(self.partner, changes)

    def test_apply_one2many(self):
        """Apply a change on a One2many field is not supported"""
        changes = [
            (
                self.field_one2many,
                [self.env.ref("base.user_root").id, self.env.ref("base.user_demo").id],
                "draft",
            )
        ]
        with self.assertRaises(NotImplementedError):
            self._create_changeset(self.partner, changes)

    def test_apply_binary(self):
        """Apply a change on a Binary field is not supported"""
        changes = [(self.field_one2many, "", "draft")]
        with self.assertRaises(NotImplementedError):
            self._create_changeset(self.partner, changes)
