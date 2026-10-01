# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.orm.model_classes import add_to_registry
from odoo.tests import common


class CommonBaseSequenceOption(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        from .base_sequence_tester import BaseSequenceTester, IrSequenceOption

        add_to_registry(cls.registry, BaseSequenceTester)
        add_to_registry(cls.registry, IrSequenceOption)
        model_name = "base.sequence.tester"
        cls.registry._setup_models__(cls.env.cr, [model_name])
        cls.registry.init_models(cls.env.cr, [model_name], {"models_to_check": True})
        cls.addClassCleanup(cls.registry.__delitem__, model_name)

        cls.test_model = cls.env[BaseSequenceTester._name]

        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "base.sequence.tester")]
        )

        # Access record:
        cls.env["ir.model.access"].create(
            {
                "name": "access.tester",
                "model_id": cls.tester_model.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )

        # Create sequence for type A and type B
        cls.ir_sequence_obj = cls.env["ir.sequence"]
        cls.ir_sequence_obj.create(
            {
                "name": "Default Sequence",
                "code": "base.sequence.tester",
                "padding": 5,
                "prefix": "DEF/",
            }
        )
        seq_a = cls.ir_sequence_obj.create(
            {
                "name": "Type A",
                "padding": 5,
                "prefix": "TYPE-A/",
            }
        )
        seq_b = cls.ir_sequence_obj.create(
            {
                "name": "Type B",
                "padding": 5,
                "prefix": "TYPE-B/",
            }
        )

        # Create sequence options for model base.sequence.tester:
        cls.base_sequence_obj = cls.env["ir.sequence.option"]
        cls.base_seq = cls.base_sequence_obj.create(
            {
                "name": "Test Model",
                "model": "base.sequence.tester",
                "use_sequence_option": True,
            }
        )
        cls.sequence_obj = cls.env["ir.sequence.option.line"]
        cls.sequence_obj.create(
            {
                "base_id": cls.base_seq.id,
                "name": "Option 1",
                "filter_domain": [("test_type", "=", "a")],
                "sequence_id": seq_a.id,
            }
        )
        cls.sequence_obj.create(
            {
                "base_id": cls.base_seq.id,
                "name": "Option 1",
                "filter_domain": [("test_type", "=", "b")],
                "sequence_id": seq_b.id,
            }
        )
