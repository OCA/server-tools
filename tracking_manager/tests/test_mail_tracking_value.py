# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestMailTracking(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailTracking = cls.env["mail.tracking.value"]

    def test_create_tracking_values_html(self):
        initial_value = "<p>Initial Value</p>"
        new_value = "<p>New Value</p>"
        col_name = "comment"
        col_info = {"type": "html"}
        record = self.env["res.partner"].create({"name": "Test Partner"})

        values = self.MailTracking._create_tracking_values(
            initial_value, new_value, col_name, col_info, record
        )

        self.assertEqual(values["old_value_char"], "Initial Value")
        self.assertEqual(values["new_value_char"], "New Value")

    def _test_create_tracking_values_property(self, values):
        property_type_mapped = {
            "char": "char",
            "boolean": "integer",
            "integer": "integer",
            "float": "float",
            "date": "datetime",
            "datetime": "datetime",
            "selection": "char",
            "tags": "char",
            "many2one": "integer",
            "many2many": "char",
        }
        test_properties_info = {
            "property_01": {"string": "property_01", "type": "char"},
            "property_02": {"string": "property_02", "type": "boolean"},
            "property_03": {"string": "property_03", "type": "integer"},
            "property_04": {"string": "property_04", "type": "float"},
            "property_05": {"string": "property_05", "type": "date"},
            "property_06": {"string": "property_06", "type": "datetime"},
            "property_07": {
                "string": "property_07",
                "type": "selection",
                "selection": [["key1", "value1"], ["key2", "value2"]],
            },
            "property_08": {"string": "property_08", "type": "tags"},
            "property_09": {
                "string": "property_09",
                "type": "many2one",
                "comodel": self.partner._name,
            },
            "property_10": {
                "string": "property_10",
                "type": "many2many",
                "comodel": self.partner._name,
            },
        }
        for p_name, col_info in test_properties_info.items():
            initial_value = values[p_name][0]
            new_value = values[p_name][1]
            res = self.MailTracking._create_tracking_values_property(
                initial_value, new_value, "title", col_info, self.partner
            )
            del res["field_info"]
            f_name = property_type_mapped[col_info["type"]]
            expected_old_value = initial_value
            expected_new_value = new_value
            if col_info["type"] == "date":
                expected_old_value = (
                    f"{expected_old_value} 00:00:00" if expected_old_value else False
                )
                expected_new_value = (
                    f"{expected_new_value} 00:00:00" if expected_new_value else False
                )
            elif col_info["type"] == "selection":
                expected_old_value = values[p_name][2]
                expected_new_value = values[p_name][3]
            elif col_info["type"] == "tags":
                expected_old_value = (
                    ", ".join(value for value in expected_old_value)
                    if expected_old_value
                    else ""
                )
                expected_new_value = (
                    ", ".join(value for value in expected_new_value)
                    if expected_new_value
                    else ""
                )
            elif col_info["type"] == "many2one":
                del res["old_value_char"]
                del res["new_value_char"]
            elif col_info["type"] == "many2many":
                comodel = self.env[col_info["comodel"]]
                expected_old_value = (
                    comodel.browse(expected_old_value) if expected_old_value else False
                )
                expected_new_value = (
                    comodel.browse(expected_new_value) if expected_new_value else False
                )
                expected_old_value = (
                    ", ".join(expected_old_value.mapped("display_name"))
                    if expected_old_value
                    else ""
                )
                expected_new_value = (
                    ", ".join(expected_new_value.mapped("display_name"))
                    if expected_new_value
                    else ""
                )
            expected_values = {
                f"old_value_{f_name}": expected_old_value,
                f"new_value_{f_name}": expected_new_value,
            }
            self.assertEqual(res, expected_values)

    def test_mail_tracking_value_properties(self):
        partner_extra = self.env["res.partner"].create({"name": "Test partner extra"})
        test_properties_01 = {
            # property: initial_value, new_value
            "property_01": ("", "value1"),
            "property_02": (False, True),
            "property_03": (0, 10),
            "property_04": (0, 10.10),
            "property_05": (False, "2025-01-01"),
            "property_06": (False, "2025-01-01 00:00:00"),
            "property_07": (False, "key1", "", "value1"),
            "property_08": (False, ["tag1", "tag2"]),
            "property_09": (False, self.partner.id),
            "property_10": (False, [self.partner.id, partner_extra.id]),
        }
        # Test all the property types using as fake title field because there is no
        # property field in base to test.
        # We do not want to create a FakeModel and add the property field in partner
        # because the partner_property module could have conflicts.
        # 1- Test the case that all the initial values were empty and now have a value
        self._test_create_tracking_values_property(test_properties_01)
        # 2- Test the case that all the initial values had something set and now have
        # a different value
        test_properties_02 = {
            # property: initial_value, new_value
            "property_01": ("value1", "value2"),
            "property_02": (True, False),
            "property_03": (10, 11),
            "property_04": (10.10, 11.10),
            "property_05": ("2025-01-01", "2025-01-02"),
            "property_06": ("2025-01-01 00:00:00", "2025-01-02 00:00:00"),
            "property_07": ("key1", "key2", "value1", "value2"),
            "property_08": (
                ["tag1", "tag2"],
                [
                    "tag1",
                ],
            ),
            "property_09": (self.partner.id, partner_extra.id),
            "property_10": (
                [self.partner.id, partner_extra.id],
                [
                    self.partner.id,
                ],
            ),
        }
        self._test_create_tracking_values_property(test_properties_02)
        # 3- Test the case that all initial values had something set and now has
        # no value
        test_properties_03 = {
            # property: initial_value, new_value
            "property_01": ("value2", ""),
            "property_02": (False, True),
            "property_03": (11, 0),
            "property_04": (11.10, 0),
            "property_05": ("2025-01-02", False),
            "property_06": ("2025-01-02 00:00:00", False),
            "property_07": ("key1", False, "value1", ""),
            "property_08": (["tag1", "tag2"], False),
            "property_09": (self.partner.id, False),
            "property_10": ([self.partner.id, partner_extra.id], False),
        }
        self._test_create_tracking_values_property(test_properties_03)
