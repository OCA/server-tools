# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError
from odoo.modules.module import get_resource_path
import base64
import io

from .fake_models import FakeModel


def load_filecontent(module, filepath, mode='rb'):
    path = get_resource_path(module, filepath)
    with io.open(path, mode) as fd:
        return fd.read()


class TestValidation(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        FakeModel._test_setup(cls.env)

        cls.model = cls.env['ir.attachment']
        cls.txt_content = b'foo'
        cls.txt_content_b64 = base64.b64encode(cls.txt_content)
        cls.pdf_content = load_filecontent(
            'base_binary_validation', 'tests/test_me_pls.pdf')
        cls.pdf_content_b64 = base64.b64encode(cls.pdf_content)

    @classmethod
    def tearDownClass(cls):
        FakeModel._test_teardown(cls.env)
        super().tearDownClass()

    def test_no_validation(self):
        att = self.model.create(
            {'name': 'Fake 1 ', 'datas': self.txt_content_b64})
        self.assertEqual(att.datas, self.txt_content_b64)
        att = self.model.create(
            {'name': 'Fake 2', 'datas': self.pdf_content_b64})
        self.assertEqual(att.datas, self.pdf_content_b64)

    def test_validation(self):
        model = self.model.with_context(allowed_mimetypes=('application/pdf'))
        with self.assertRaises(ValidationError):
            model.create({'name': 'Fake 1 ', 'datas': self.txt_content_b64})
        att = model.create(
            {'name': 'Fake 2', 'datas': self.pdf_content_b64})
        self.assertEqual(att.datas, self.pdf_content_b64)

    def test_field_validation(self):
        rec = self.env['binary.fake.model'].create({'name': 'Foo'})
        with self.assertRaises(ValidationError):
            rec.pdf_file = self.txt_content_b64
        rec.txt_file = self.txt_content_b64
        self.assertEqual(rec.txt_file, self.txt_content_b64)
        rec.pdf_file = self.pdf_content
        self.assertEqual(rec.pdf_file, self.pdf_content)
