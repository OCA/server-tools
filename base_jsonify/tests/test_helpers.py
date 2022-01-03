# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestJsonifyHelpers(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "My Partner",
            }
        )
        cls.children = cls.env["res.partner"].create(
            [
                {"parent_id": cls.partner.id, "name": "Child 1"},
                {"parent_id": cls.partner.id, "name": "Child 2"},
            ]
        )

    def test_helper_m2o_to_id(self):
        child = self.children[0]
        self.assertEqual(
            child._jsonify_m2o_to_id("parent_id"),
            child.parent_id.id,
        )

    def test_helper_m2m_to_ids(self):
        self.assertEqual(
            self.partner._jsonify_x2m_to_ids("child_ids"),
            self.partner.child_ids.ids,
        )

    def test_helper_format_duration(self):
        # credit_limit is not intended for this, but it's a float field in core
        # any float field does the trick here
        self.partner.credit_limit = 15.5
        self.assertEqual(
            self.partner._jsonify_format_duration("credit_limit"),
            "15:30",
        )
