# Copyright 2023 Omal Bastin (o4odoo@gmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo_test_helper import FakeModelLoader

from odoo.tests import TransactionCase
from odoo.tools.misc import file_open


class TestBaseException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        img_path = "product/static/img/product_product_11-image.png"
        img_content = base64.b64encode(file_open(img_path, "rb").read())
        cls.transparent_image = (  # 1x1 Transparent GIF
            b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        )
        cls.grey_image = (  # 1x1 Grey GIF
            b"R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw =="
        )
        cls.black_image = (  # 1x1 Black GIF
            b"R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs="
        )
        from .test_images import ImageOwnerTest

        cls.loader.update_registry((ImageOwnerTest,))
        cls.img_owner = cls.env["base_multi_image.owner.test"].create(
            {
                "name": "Test Multiple Imges",
                "image_ids": [
                    (
                        0,
                        0,
                        {
                            "storage": "filestore",
                            "name": "Image 1",
                            "attachment_image": img_content,
                            "owner_model": "base_multi_image.owner.test",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "storage": "filestore",
                            "name": "Image 2",
                            "attachment_image": cls.black_image,
                            "owner_model": "product.template",
                        },
                    ),
                ],
            }
        )

    def test_all_images(self):
        self.assertEqual(len(self.img_owner.image_ids), 2)

    def test_add_image(self):
        self.img_owner.image_ids = [
            (0, 0, {"storage": "filestore", "attachment_image": self.grey_image})
        ]
        self.img_owner.refresh()
        self.assertEqual(len(self.img_owner.image_ids), 3)

    def test_remove_image(self):
        self.img_owner.image_ids = [(3, self.img_owner.image_ids[0].id)]
        self.img_owner.refresh()
        self.assertEqual(len(self.img_owner.image_ids), 2)

    def test_remove_image_all(self):
        self.img_owner.image_ids = [(3, self.img_owner.image_ids[0].id)]
        self.img_owner.image_ids = [(3, self.img_owner.image_ids[0].id)]
        self.img_owner.refresh()
        self.assertEqual(len(self.img_owner.image_ids), 1)

    def test_edit_image_(self):
        text = "Test name changed"
        self.img_owner.image_ids[0].name = text
        self.img_owner.refresh()
        self.assertEqual(self.img_owner.image_ids[0].name, text)
