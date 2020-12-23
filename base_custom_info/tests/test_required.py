# Copyright 2020 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class PartnerCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(PartnerCase, self).setUp(*args, **kwargs)
        self.agrolait = self.env.ref("base.res_partner_2")
        self.template = self.env["custom.info.template"].create(
            {
                "name": "TEST Template",
                "model_id": self.env.ref("base.model_res_partner").id,
                "property_ids": [
                    (0, 0, {"name": "Property", "widget": "char", "required": True})
                ],
            }
        )

    def test_required_form_failure(self):
        with Form(self.agrolait) as f:
            self.assertFalse(f.custom_info_template_id)
            self.assertFalse(f.custom_info_ids)
            f.custom_info_template_id = self.template
            self.assertTrue(f.custom_info_ids)
            with self.assertRaises(AssertionError):
                f.save()
            f.custom_info_template_id = self.env["custom.info.template"]
            self.assertFalse(f.custom_info_ids)

    def test_required_failure(self):
        self.assertFalse(self.agrolait.custom_info_template_id)
        self.assertFalse(self.agrolait.custom_info_ids)
        self.agrolait.custom_info_template_id = self.template
        with self.assertRaises(ValidationError):
            self.agrolait._onchange_custom_info_template_id()

    def test_required(self):
        with Form(self.agrolait) as f:
            self.assertFalse(f.custom_info_template_id)
            self.assertFalse(f.custom_info_ids)
            f.custom_info_template_id = self.template
            self.assertEqual(1, len(f.custom_info_ids))
            with f.custom_info_ids.edit(0) as info:
                info.value_str = "HELLO"
        self.assertTrue(self.agrolait.custom_info_ids.value)
