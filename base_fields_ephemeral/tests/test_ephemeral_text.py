# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.tests.common import SavepointCase

from ..fields import EphemeralText
from .common import EphemeralFieldTester as EphemeralFieldTesterOrig


class EphemeralFieldTester(models.Model):
    _inherit = 'ephemeral.field.tester'

    field = EphemeralText()


class TestEphemeralText(SavepointCase):

    @classmethod
    def _init_test_model(cls, model_cls, model_name):
        """ It builds a model from model_cls in order to test abstract models.
        Note that this does not actually create a table in the database, so
        there may be some unidentified edge cases.
        Args:
            model_cls (odoo.models.BaseModel): Class of model to initialize
        Returns:
            odoo.models.BaseModel: Instance
        """
        registry = cls.env.registry
        cr = cls.env.cr
        inst = model_cls._build_model(registry, cr)
        model = cls.env[model_name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        return inst

    @classmethod
    def setUpClass(cls):
        super(TestEphemeralText, cls).setUpClass()
        cls.env.registry.enter_test_mode()
        cls._init_test_model(
            EphemeralFieldTesterOrig, EphemeralFieldTesterOrig._name,
        )
        cls._init_test_model(
            EphemeralFieldTester, EphemeralFieldTester._inherit,
        )
        cls.test_model = cls.env[EphemeralFieldTester._inherit]

    @classmethod
    def tearDownClass(cls):
        cls.env.registry.leave_test_mode()
        super(TestEphemeralText, cls).tearDownClass()

    def setUp(self):
        super(TestEphemeralText, self).setUp()
        self.secure = 'This is secure text'
        self.insecure = 'This is control text'
        self.test_record = self.test_model.create({
            'field': self.secure,
            'control': self.insecure,
        })

    def test_secure_in_cache(self):
        """ The secure text should be usable in the cache. """
        self.assertEqual(
            self.test_record.field, self.secure,
        )

    def test_field_convert_to_write(self):
        """ It should return False for convert_to_write on ephemeral field. """
        field = self.test_record._fields['field']
        self.assertFalse(field.convert_to_write(self.secure))
