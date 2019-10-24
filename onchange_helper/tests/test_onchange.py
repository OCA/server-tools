# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2019 ACSONE SA/NV
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock
import odoo.tests.common as common
from odoo import api, models


class ResPartnerTester(models.Model):
    _inherit = "res.partner"
    _name = "res.partner"

    @api.onchange("name")
    def _onchange_name_test(self):
        """
        When the name change, assign every existing partner category
        on the partner.
        This onchange is used to test behavior of this module for M2M fields.
        :return:
        """
        self.category_id = self.env['res.partner.category'].search([], limit=2)


class TestOnchange(common.TransactionCase):

    def _init_test_model(self, model_cls):
        model_cls._build_model(self.registry, self.cr)
        model = self.env[model_cls._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        return model

    def setUp(self):
        super(TestOnchange, self).setUp()
        self.registry.enter_test_mode()
        self.old_cursor = self.cr
        self.cr = self.registry.cursor()
        self.env = api.Environment(self.cr, self.uid, {})
        self.test_model = self._init_test_model(ResPartnerTester)

    def tearDown(self):
        self.registry.leave_test_mode()
        self.cr = self.old_cursor
        self.env = api.Environment(self.cr, self.uid, {})
        super(TestOnchange, self).tearDown()

    def test_playing_onchange_m2m(self):
        """
        Test if the onchange fill correctly M2M fields.
        :return:
        """
        values = {
            "name": "Balthazar Melchior Gaspard",
        }
        expected_categs = self.env['res.partner.category'].search([], limit=2)
        # We should have some categs for this test
        self.assertTrue(expected_categs)
        # We have to ensure categs are into cache. So just load the name.
        expected_categs.mapped("name")
        expected_result = [(5,)]
        expected_result.extend([(4, c.id) for c in expected_categs])
        result = self.env['res.partner'].play_onchanges(values, values.keys())
        self.assertEqual(result["category_id"], expected_result)

    def test_playing_onchange_on_model(self):
        res_partner = self.env["res.partner"]
        with mock.patch.object(
            res_partner.__class__, "write"
        ) as patched_write:
            result = self.env["res.partner"].play_onchanges(
                {"company_type": "company"}, ["company_type"]
            )
            patched_write.assert_not_called()
        self.assertEqual(result["is_company"], True)

    def test_playing_onchange_on_record(self):
        company = self.env.ref("base.main_company")
        with mock.patch.object(company.__class__, "write") as patched_write:
            result = company.play_onchanges(
                {"email": "contact@akretion.com"}, ["email"]
            )
            patched_write.assert_not_called()
        modified_fields = set(result.keys())
        self.assertSetEqual(
            modified_fields, {"rml_footer", "rml_footer_readonly"}
        )
        self.assertEqual(
            result["rml_footer"],
            u"Phone: +1 555 123 8069 | Email: contact@akretion.com | "
            u"Website: http://www.example.com",
        )
        self.assertEqual(result["rml_footer_readonly"], result["rml_footer"])

        # check that the original record is not modified
        self.assertFalse(company._get_dirty())
        self.assertEqual(company.email, u"info@yourcompany.example.com")

    def test_onchange_record_with_dirty_field(self):
        company = self.env.ref("base.main_company")
        company._set_dirty("name")
        self.assertListEqual(company._get_dirty(), ["name"])
        company.play_onchanges({"email": "contact@akretion.com"}, ["email"])
        self.assertListEqual(company._get_dirty(), ["name"])

    def test_onchange_wrong_key(self):
        res_partner = self.env["res.partner"]
        with mock.patch.object(
                res_partner.__class__, "write"
        ) as patched_write:
            # we specify a wrong field name... This field should be
            # ignored
            result = self.env["res.partner"].play_onchanges(
                {"company_type": "company"}, ["company_type", "wrong_key"]
            )
            patched_write.assert_not_called()
        self.assertEqual(result["is_company"], True)
