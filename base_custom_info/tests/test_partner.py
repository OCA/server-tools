# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.exceptions import AccessError, ValidationError
from openerp.tests.common import TransactionCase


class PartnerCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(PartnerCase, self).setUp(*args, **kwargs)
        self.agrolait = self.env.ref("base.res_partner_2")
        self.tpl = self.env.ref("base_custom_info.tpl_smart")
        self.demouser = self.env.ref("base.user_demo")

    def set_custom_info_for_agrolait(self):
        """Used when you need to use some created custom info."""
        self.agrolait.custom_info_template_id = self.tpl
        self.env["custom.info.value"].create({
            "res_id": self.agrolait.id,
            "property_id": self.env.ref("base_custom_info.prop_haters").id,
            "value_int": 5,
        })

    def test_access_granted(self):
        """Access to the model implies access to custom info."""
        # Demo user has contact creation permissions by default
        agrolait = self.agrolait.sudo(self.demouser)
        agrolait.custom_info_template_id = self.tpl
        agrolait.env["custom.info.value"].create({
            "res_id": agrolait.id,
            "property_id":
                agrolait.env.ref("base_custom_info.prop_weaknesses").id,
            "value_id": agrolait.env.ref("base_custom_info.opt_food").id,
        })
        agrolait.custom_info_template_id.property_ids[0].name = "Changed!"
        agrolait.env.ref("base_custom_info.opt_food").name = "Changed!"

    def test_access_denied(self):
        """Forbidden access to the model forbids it to custom info."""
        # Remove permissions to demo user
        self.demouser.groups_id = self.env.ref("base.group_portal")

        agrolait = self.agrolait.sudo(self.demouser)
        with self.assertRaises(AccessError):
            agrolait.custom_info_template_id = self.tpl

        with self.assertRaises(AccessError):
            agrolait.env["custom.info.value"].create({
                "res_id": agrolait.id,
                "property_id":
                    agrolait.env.ref("base_custom_info.prop_weaknesses").id,
                "value_id": agrolait.env.ref("base_custom_info.opt_food").id,
            })

        with self.assertRaises(AccessError):
            agrolait.custom_info_template_id.property_ids[0].name = "Changed!"

        with self.assertRaises(AccessError):
            agrolait.env.ref("base_custom_info.opt_food").name = "Changed!"

    def test_apply_unapply_template(self):
        """(Un)apply a template to a owner and it gets filled."""
        # Applying a template autofills the values
        self.agrolait.custom_info_template_id = self.tpl
        with self.env.do_in_onchange():
            self.agrolait._onchange_custom_info_template_id()
        self.assertEqual(
            len(self.agrolait.custom_info_ids),
            len(self.tpl.property_ids))
        self.assertEqual(
            self.agrolait.custom_info_ids.mapped("property_id"),
            self.tpl.property_ids)

        # Unapplying a template empties the values
        self.agrolait.custom_info_template_id = False
        self.agrolait._onchange_custom_info_template_id()
        self.assertFalse(self.agrolait.custom_info_template_id)

    def test_template_model_and_model_id_match(self):
        """Template's model and model_id fields match."""
        self.assertEqual(self.tpl.model, self.tpl.model_id.model)
        self.tpl.model = "res.users"
        self.assertEqual(self.tpl.model, self.tpl.model_id.model)

    def test_template_model_must_exist(self):
        """Cannot create templates for unexisting models."""
        with self.assertRaises(ValidationError):
            self.tpl.model = "yabadabaduu"

    def test_change_used_model_fails(self):
        """If a template's model is already used, you cannot change it."""
        self.set_custom_info_for_agrolait()
        with self.assertRaises(ValidationError):
            self.tpl.model = "res.users"

    def test_owners_selection(self):
        """Owners selection includes only the required matches."""
        choices = dict(self.env["custom.info.value"]._selection_owner_id())
        self.assertIn("res.partner", choices)
        self.assertNotIn("ir.model", choices)
        self.assertNotIn("custom.info.property", choices)
        self.assertNotIn("custom.info", choices)

    def test_owner_id(self):
        """Check the computed owner id for a value."""
        self.set_custom_info_for_agrolait()
        self.assertEqual(self.agrolait.custom_info_ids.owner_id, self.agrolait)

    def test_get_custom_info_value(self):
        """Check the custom info getter helper works fine."""
        self.set_custom_info_for_agrolait()
        result = self.agrolait.get_custom_info_value(
            self.env.ref("base_custom_info.prop_haters"))
        self.assertEqual(result.field_type, "int")
        self.assertEqual(result.field_name, "value_int")
        self.assertEqual(result[result.field_name], 5)
        self.assertEqual(result.value_int, 5)
        self.assertEqual(result.value, "5")
