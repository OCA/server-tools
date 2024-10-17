# Copyright 2023 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo_test_helper import FakeModelLoader

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class PartnerCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Images were generated with https://yulvil.github.io/gopherjs/02/
        Configuration used: 24, 24, 4
        """
        super().setUpClass()
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")])
        cls.partner_1 = cls.env.ref("base.res_partner_main1")
        cls.partner_2 = cls.env.ref("base.res_partner_main2")
        cls.partner_2_image = cls.partner_2.image_1920

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .res_partner import ResPartner

        cls.loader.update_registry([ResPartner])

        cls.logo_1 = b"""iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAIAAABvFaqvAAAAeUlEQV
R4nGK5IPCCARU8ylyKJnIjiB1NJKrlBpoIEwOVwKhBhAGjU40JmtDk4DVoIurLrqKJKHnY08pFowYRB
iwdhfJoQtPrudFEcpyfookkiRvTykWjBhEGjEoJfWhCV2eIooncS7uDJnL+zS9auWjUIMIAEAAA///9
4xeBy0j8PAAAAABJRU5ErkJggg=="""
        cls.logo_2 = b"""iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAIAAABvFaqvAAAAeUlEQV
R4nGJxDFzAgAr6+0+giYQZJ6CJ+CjxoYkwMVAJjBpEGLBM4fqPJvTTdQuaSO2VXjSR0z2stHLRqEGEA
aOJqBCa0ETTyWgiKUe2oYl4lYTSykWjBhEGjMX79qIJ3cl7iyYitM4JTaSCgZ1WLho1iDAABAAA//+v
ThXENXIVmwAAAABJRU5ErkJggg=="""

        # Default first as it's mandatory
        cls.conditional_image_2 = cls.env["conditional.image"].create(
            {
                "name": "Global logo",
                "default": True,
                "model_id": cls.partner_model.id,
                "image_1920": cls.logo_2,
            }
        )
        cls.conditional_image_1 = cls.env["conditional.image"].create(
            {
                "name": "Chester Reed logo",
                "default": False,
                "model_id": cls.partner_model.id,
                "selector": f"object.id == {cls.partner_1.id}",
                "image_1920": cls.logo_1,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_unique_default_partner_image(self):
        self.assertRaises(
            ValidationError,
            self.env["conditional.image"].create,
            {
                "name": "Dual default logo",
                "default": True,
                "model_id": self.partner_model.id,
                "image_1920": self.logo_2,
            },
        )

    def test_missing_default_partner_image(self):
        self.conditional_image_1.unlink()
        self.conditional_image_2.unlink()
        self.assertRaises(
            ValidationError,
            self.env["conditional.image"].create,
            {
                "name": "Dual default logo",
                "default": False,
                "model_id": self.partner_model.id,
                "image_1920": self.logo_2,
            },
        )

    def test_default_partner_image(self):
        self.assertEqual(self.partner_2.image_1920, self.logo_2)

    def test_custom_partner_image(self):
        self.assertEqual(self.partner_1.image_1920, self.logo_1)
