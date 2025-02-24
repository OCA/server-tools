# Copyright 2023 Omal Bastin (o4odoo@gmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import os
import tempfile

from odoo_test_helper import FakeModelLoader

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestMultiImage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        # img_path = "product/static/img/product_product_11-image.png"
        # img_content = base64.b64encode(file_open(img_path, "rb").read())
        cls.transparent_image = (  # 1x1 Transparent GIF
            b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        )
        cls.grey_image = (  # 1x1 Grey GIF
            b"R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="
        )
        cls.black_image = (  # 1x1 Black GIF
            b"R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs="
        )
        from .test_images import ImageOwnerTest

        cls.loader.update_registry((ImageOwnerTest,))
        for model in cls.registry.values():
            if model._name not in cls.attrs_before:
                cls.attrs_before[model._name] = {
                    *vars(model),
                    "__annotations__",
                    "_rec_name",
                    "_active_name",
                }
        cls.img_owner = cls.env["base_multi_image.owner.test"].create(
            {
                "name": "Test Multiple Imges",
                "image_ids": [
                    Command.create(
                        {
                            "storage": "filestore",
                            "name": "Image 1",
                            "attachment_image": cls.transparent_image,
                            "owner_model": "base_multi_image.owner.test",
                        },
                    ),
                    Command.create(
                        {
                            "storage": "filestore",
                            "name": "Image 2",
                            "attachment_image": cls.black_image,
                            "owner_model": "base_multi_image.owner.test",
                        },
                    ),
                ],
            }
        )
        cls.img_owner.invalidate_recordset()

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_all_images(self):
        self.assertEqual(len(self.img_owner.image_ids), 2)

    def test_add_image(self):
        self.img_owner.image_ids = [
            Command.create(
                {
                    "storage": "filestore",
                    "attachment_image": self.grey_image,
                    "name": "Image 3",
                    "owner_model": "base_multi_image.owner.test",
                },
            )
        ]
        self.img_owner.invalidate_recordset()
        self.assertEqual(len(self.img_owner.image_ids), 3)

    def test_remove_image(self):
        self.img_owner.image_ids = [(3, self.img_owner.image_ids[0].id)]
        self.img_owner.invalidate_recordset()
        self.assertEqual(len(self.img_owner.image_ids), 1)

    def test_remove_image_all(self):
        self.img_owner.image_ids = [(3, self.img_owner.image_ids[0].id)]
        self.img_owner.image_ids = [(3, self.img_owner.image_ids[1].id)]
        self.img_owner.invalidate_recordset()
        self.assertEqual(len(self.img_owner.image_ids), 0)

    def test_edit_image(self):
        text = "Test name changed"
        self.img_owner.image_ids[0].name = text
        self.assertEqual(self.img_owner.image_ids[0].name, text)

    def test_storage_db(self):
        image = self.env["base_multi_image.image"].create(
            {
                "storage": "db",
                "file_db_store": self.transparent_image,
                "name": "DB Image",
                "owner_model": "base_multi_image.owner.test",
                "owner_id": self.img_owner.id,
            }
        )
        self.assertEqual(image.image_1920, self.transparent_image)

    def test_storage_attachment(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "Test Attachment",
                "datas": self.black_image,
                "mimetype": "image/gif",
                "res_model": "base_multi_image.owner.test",
                "res_id": self.img_owner.id,
            }
        )
        image = self.env["base_multi_image.image"].create(
            {
                "storage": "attachment",
                "attachment_id": attachment.id,
                "owner_model": "base_multi_image.owner.test",
                "owner_id": self.img_owner.id,
            }
        )
        self.assertEqual(image.image_1920, self.black_image)
        image._onchange_attachmend_id()
        self.assertEqual(image.name, self.img_owner.name)

    def test_storage_url(self):
        with self.assertRaises(ValidationError):  # ValidationError
            self.env["base_multi_image.image"].create(
                {
                    "storage": "url",
                    "name": "URL Image Invalid",
                    "owner_model": "base_multi_image.owner.test",
                    "owner_id": self.img_owner.id,
                }
            )
        image = self.env["base_multi_image.image"].new(
            {
                "storage": "url",
                "url": "https://example.com/test.png",
            }
        )
        image._onchange_url()
        self.assertEqual(image.extension, ".png")
        self.assertEqual(image.name, "Test")

    @mute_logger("odoo.addons.base_multi_image.models.image")
    def test_storage_file(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(base64.b64decode(self.grey_image))
            path = f.name
        try:
            image = self.env["base_multi_image.image"].create(
                {
                    "storage": "file",
                    "path": path,
                    "name": "File Image",
                    "owner_model": "base_multi_image.owner.test",
                    "owner_id": self.img_owner.id,
                }
            )
            self.assertEqual(
                image.image_1920.replace(b"\n", b""), self.grey_image.replace(b" ", b"")
            )
            image_onchange = self.env["base_multi_image.image"].new(
                {
                    "storage": "file",
                    "path": path,
                }
            )
            image_onchange._onchange_path()
            self.assertTrue(image_onchange.name)
            self.assertEqual(image_onchange.extension, ".png")
            image.path = "/invalid/path/to/image.png"
            self.assertFalse(image.image_1920)
        finally:
            if os.path.exists(path):
                os.remove(path)
        with self.assertRaises(ValidationError):
            self.env["base_multi_image.image"].create(
                {
                    "storage": "file",
                    "name": "Missing Path",
                    "owner_model": "base_multi_image.owner.test",
                    "owner_id": self.img_owner.id,
                }
            )

    def test_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["base_multi_image.image"].create(
                {
                    "storage": "db",
                    "name": "Missing DB Content",
                    "owner_model": "base_multi_image.owner.test",
                    "owner_id": self.img_owner.id,
                }
            )
        with self.assertRaises(ValidationError):
            self.env["base_multi_image.image"].create(
                {
                    "storage": "attachment",
                    "name": "Missing Attachment",
                    "owner_model": "base_multi_image.owner.test",
                    "owner_id": self.img_owner.id,
                }
            )
        with self.assertRaises(ValidationError):
            self.env["base_multi_image.image"].create(
                {
                    "storage": "filestore",
                    "name": "Missing Filestore",
                    "owner_model": "base_multi_image.owner.test",
                    "owner_id": self.img_owner.id,
                }
            )

    def test_owner_compatibility(self):
        self.assertEqual(self.img_owner.image_1920, self.transparent_image)
        self.img_owner.image_1920 = self.grey_image
        self.assertEqual(self.img_owner.image_ids[0].image_1920, self.grey_image)
        new_owner = self.env["base_multi_image.owner.test"].create(
            {
                "name": "New Owner",
            }
        )
        new_owner.image_1920 = self.black_image
        new_owner.invalidate_recordset()
        self.assertEqual(len(new_owner.image_ids), 1)
        self.assertEqual(new_owner.image_ids[0].image_1920, self.black_image)
        new_owner.image_1920 = False
        self.assertEqual(len(new_owner.image_ids), 0)

    def test_onchange_filename(self):
        image = self.env["base_multi_image.image"].new(
            {
                "filename": "my_image.jpg",
            }
        )
        image._onchange_filename()
        self.assertEqual(image.name, "My image")
        self.assertEqual(image.extension, ".jpg")
