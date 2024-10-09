# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import tagged

from .common import CommonBaseSequenceOption


@tagged("post_install", "-at_install")
class TestBaseSequenceTester(CommonBaseSequenceOption):
    def test_sequence_options(self):
        """
        Test 3 cases,
        1. Default
        2. Sequence Type A
        3. Sequence Type B
        """
        # 1. Default
        rec = self.test_model.create({})
        self.assertIn("DEF/", rec.name)
        # 2. Type A
        rec = self.test_model.create({"test_type": "a"})
        self.assertIn("TYPE-A/", rec.name)
        # 3. Type B
        rec = self.test_model.create({"test_type": "b"})
        self.assertIn("TYPE-B/", rec.name)
        # Not useing the sequence
        self.base_seq.use_sequence_option = False
        rec = self.test_model.create({"test_type": "b"})
        self.assertIn("DEF/", rec.name)
