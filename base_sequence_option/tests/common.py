# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo_test_helper import FakeModelLoader

from odoo.tests import common


class CommonBaseSequenceOption(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from .base_sequence_tester import BaseSequenceTester, IrSequenceOption

        self.loader.update_registry((BaseSequenceTester, IrSequenceOption))

        self.test_model = self.env[BaseSequenceTester._name]

        self.tester_model = self.env["ir.model"].search(
            [("model", "=", "base.sequence.tester")]
        )

        # Access record:
        self.env["ir.model.access"].create(
            {
                "name": "access.tester",
                "model_id": self.tester_model.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )

        # Create sequence for type A and type B
        self.ir_sequence_obj = self.env["ir.sequence"]
        self.ir_sequence_obj.create(
            {
                "name": "Default Sequence",
                "code": "base.sequence.tester",
                "padding": 5,
                "prefix": "DEF/",
            }
        )
        seq_a = self.ir_sequence_obj.create(
            {
                "name": "Type A",
                "padding": 5,
                "prefix": "TYPE-A/",
            }
        )
        seq_b = self.ir_sequence_obj.create(
            {
                "name": "Type B",
                "padding": 5,
                "prefix": "TYPE-B/",
            }
        )

        # Create sequence options for model base.sequence.tester:
        self.base_sequence_obj = self.env["ir.sequence.option"]
        self.base_seq = self.base_sequence_obj.create(
            {
                "name": "Test Model",
                "model": "base.sequence.tester",
                "use_sequence_option": True,
            }
        )
        self.sequence_obj = self.env["ir.sequence.option.line"]
        self.sequence_obj.create(
            {
                "base_id": self.base_seq.id,
                "name": "Option 1",
                "filter_domain": [("test_type", "=", "a")],
                "sequence_id": seq_a.id,
            }
        )
        self.sequence_obj.create(
            {
                "base_id": self.base_seq.id,
                "name": "Option 1",
                "filter_domain": [("test_type", "=", "b")],
                "sequence_id": seq_b.id,
            }
        )

    def tearDown(self):
        self.loader.restore_registry()
        return super().tearDown()
