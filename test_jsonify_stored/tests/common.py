# Copyright 2020 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class TestJsonifyMixin(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestJsonifyMixin, cls).setUpClass()
        speedup_dict = {"tracking_disable": True, "no_reset_password": True}
        cls.env = cls.env(context=dict(cls.env.context, **speedup_dict))

        cls.user_1 = cls.env.user
        vals_record_1 = {
            "boolean": True,
            "char": "a",
            "float": 3,
            "user_id": cls.user_1.id,
        }
        cls.record_1 = cls.env["test.jsonify.stored"].create(vals_record_1)
        cls.user_2 = cls.env["res.users"].create({"name": "U", "login": "U"})
        vals_record_2 = {
            "boolean": False,
            "char": "b",
            "float": 5,
            "user_id": cls.user_2.id,
        }
        cls.record_2 = cls.env["test.jsonify.stored"].create(vals_record_2)

        cls.records = cls.record_1 + cls.record_2

        cls.export = cls.record_1._jsonify_get_export()
