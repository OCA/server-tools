# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from logging import getLogger

from odoo_test_helper import FakeModelLoader

from odoo import api, fields, models
from odoo.tests import TransactionCase
from odoo.tools.misc import mute_logger

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestRecordDiffCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Setup env
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env

        # ``_register_hook()`` is usually called at the end of the test process, but
        # we need to be able to test it here
        cls.env["base"]._register_hook()

        # Load test model
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        class BWDTestModel(models.Model):
            _name = "bwd.test.model"
            _description = "Base Write Diff - Test Model"
            _test_logger = getLogger("bwd.test.model.log")

            # To test a non-relational field
            name = fields.Char()
            # To test single-relational fields
            m2o_id = fields.Many2one("bwd.test.model")
            # To test multi-relational fields
            o2m_ids = fields.One2many("bwd.test.model", inverse_name="m2o_id")
            m2m_ids = fields.Many2many("bwd.test.model", "test_rel", "id_1", "id_2")
            # To test computed fields
            # ``perimeter``: computed, stored field that depends on stored fields
            # ``area``: computed, non-stored field that depends on stored fields
            # ``volume``: computed, non-stored field that depends on non-stored fields
            length = fields.Integer()  # pylint: disable=W8105  (Pylint complains this?)
            width = fields.Integer()
            height = fields.Integer()
            perimeter = fields.Integer(compute="_compute_perimeter", store=True)
            area = fields.Integer(compute="_compute_area", store=False)
            volume = fields.Integer(compute="_compute_volume", store=False)

            @api.depends("length", "width")
            def _compute_perimeter(self):
                self._test_logger.warning("Computing perimeter")
                for rec in self:
                    rec.perimeter = 2 * (rec.length + rec.width)

            @api.depends("length", "width")
            def _compute_area(self):
                self._test_logger.warning("Computing area")
                for rec in self:
                    rec.area = rec.length * rec.width

            @api.depends("area", "height")
            def _compute_volume(self):
                self._test_logger.warning("Computing volume")
                for rec in self:
                    rec.volume = rec.area * rec.height

        cls.loader.update_registry([BWDTestModel])

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def _create_records(self, count=1):
        records = self.env["bwd.test.model"].create([{} for _ in range(1, count + 1)])
        for rec in records:
            rec.name = f"Record {rec.id}"
        return records


class TestRecordDiff(TestRecordDiffCommon):
    @mute_logger("bwd.test.model.log")
    def test_00_get_write_diff_values_simple(self):
        """Test ``_get_write_diff_values()`` on fields that are not multi-relational"""
        record = self._create_records()
        # Try to write the same value on non-relational field
        # => ``_get_write_diff_values()`` returns an empty dict
        vals = {"name": record.name}
        self.assertEqual(record._get_write_diff_values(vals), {})
        # Try to write another value on non-relational field
        # => ``_get_write_diff_values()`` returns the same dict
        vals = {"name": record.name + " something else"}
        self.assertEqual(record._get_write_diff_values(vals), vals)
        # Try to write the same value on M2O field
        # => ``_get_write_diff_values()`` returns an empty dict
        vals = {"m2o_id": record.m2o_id.id}
        self.assertEqual(record._get_write_diff_values(vals), {})
        # Try to write another value on M2O field
        # => ``_get_write_diff_values()`` returns the same dict
        vals = {"m2o_id": self._create_records().id}
        self.assertEqual(record._get_write_diff_values(vals), vals)

    @mute_logger("bwd.test.model.log")
    def test_10_get_write_diff_values_x2many_command_create(self):
        """Test ``_get_write_diff_values()`` on fields.Command.create()

        ``_get_write_diff_values()`` always returns the original dict, even after the
        corecords are actually created (because the values will create a new, different
        corecord if used on ``write()`` again)
        """
        record = self._create_records()
        vals = {
            "o2m_ids": [fields.Command.create({"name": "O2M Co-record"})],
            "m2m_ids": [fields.Command.create({"name": "M2M Co-record"})],
        }
        self.assertEqual(record._get_write_diff_values(vals), vals)
        record.write(vals)  # Do the real update => the diff is not empty anyway
        self.assertEqual(record._get_write_diff_values(vals), vals)

    @mute_logger("bwd.test.model.log")
    def test_11_get_write_diff_values_x2many_command_update(self):
        """Test ``_get_write_diff_values()`` on fields.Command.update()

        ``_get_write_diff_values()`` returns only the subset of IDs/values that should
        be updated
        """
        record = self._create_records()
        # Create and assign 2 corecords to each X2M field
        record.o2m_ids = o2m_corecords = self._create_records(2)
        record.m2m_ids = m2m_corecords = self._create_records(2)
        # Set vals to update 1 corecord on each X2M field
        vals = {
            "o2m_ids": [
                fields.Command.update(o2m_corecords[0].id, {"name": "O2M Corec"}),
                fields.Command.update(
                    o2m_corecords[1].id, {"name": o2m_corecords[1].name}
                ),
            ],
            "m2m_ids": [
                fields.Command.update(
                    m2m_corecords[0].id, {"name": m2m_corecords[0].name}
                ),
                fields.Command.update(m2m_corecords[1].id, {"name": "M2M Corec"}),
            ],
        }
        # The diff should include only the IDs we want to update, and the fields we are
        # actually different on them
        self.assertEqual(
            record._get_write_diff_values(vals),
            {
                "o2m_ids": [
                    fields.Command.update(o2m_corecords[0].id, {"name": "O2M Corec"})
                ],
                "m2m_ids": [
                    fields.Command.update(m2m_corecords[1].id, {"name": "M2M Corec"})
                ],
            },
        )
        record.write(vals)  # Do the real update => the diff should be empty now
        self.assertEqual(record._get_write_diff_values(vals), {})

    @mute_logger("bwd.test.model.log")
    def test_12_get_write_diff_values_x2many_command_delete(self):
        """Test ``_get_write_diff_values()`` on fields.Command.delete()

        ``_get_write_diff_values()`` returns only the subset of IDs that should be
        deleted/unlinked
        """
        record = self._create_records()
        # Create and assign 2 corecords to each X2M field
        record.o2m_ids = o2m_corecords = self._create_records(2)
        record.m2m_ids = m2m_corecords = self._create_records(2)
        # Set vals to delete 1 corecord in each X2M field
        vals = {
            "o2m_ids": [fields.Command.delete(o2m_corecords[0].id)],
            "m2m_ids": [fields.Command.delete(m2m_corecords[1].id)],
        }
        # The diff should include only the IDs we want to delete
        self.assertEqual(
            record._get_write_diff_values(vals),
            # Odoo assigns command "delete" or "unlink" according to the field type
            # and its definition (not important for our purposes here)
            {
                "o2m_ids": [fields.Command.delete(o2m_corecords[0].id)],
                "m2m_ids": [fields.Command.unlink(m2m_corecords[1].id)],
            },
        )
        record.write(vals)  # Do the real update => the diff should be empty now
        self.assertEqual(record._get_write_diff_values(vals), {})

    @mute_logger("bwd.test.model.log")
    def test_13_get_write_diff_values_x2many_command_unlink(self):
        """Test ``_get_write_diff_values()`` on fields.Command.unlink()

        ``_get_write_diff_values()`` returns only the subset of IDs that should be
        deleted/unlinked
        """
        record = self._create_records()
        # Create and assign 2 corecords to each X2M field
        record.o2m_ids = o2m_corecords = self._create_records(2)
        record.m2m_ids = m2m_corecords = self._create_records(2)
        # Set vals to unlink 1 corecord in each X2M field
        vals = {
            "o2m_ids": [fields.Command.unlink(o2m_corecords[0].id)],
            "m2m_ids": [fields.Command.unlink(m2m_corecords[1].id)],
        }
        # The diff should include only the IDs we want to unlink
        self.assertEqual(
            record._get_write_diff_values(vals),
            # Odoo assigns command "delete" or "unlink" according to the field type
            # and its definition (not important for our purposes here)
            {
                "o2m_ids": [fields.Command.delete(o2m_corecords[0].id)],
                "m2m_ids": [fields.Command.unlink(m2m_corecords[1].id)],
            },
        )
        record.write(vals)  # Do the real update => the diff should be empty now
        self.assertEqual(record._get_write_diff_values(vals), {})

    @mute_logger("bwd.test.model.log")
    def test_14_get_write_diff_values_x2many_command_link(self):
        """Test ``_get_write_diff_values()`` on fields.Command.link()

        ``_get_write_diff_values()`` returns only the subset of IDs that should be
        linked
        """
        record = self._create_records()
        # Create 2 corecords
        o2m_corecords = self._create_records(2)
        m2m_corecords = self._create_records(2)
        # Assign 1 corecord to each X2M field
        record.write(
            {
                "o2m_ids": [fields.Command.set(o2m_corecords[0].ids)],
                "m2m_ids": [fields.Command.set(m2m_corecords[1].ids)],
            }
        )
        # Set vals to link all corecords on each X2M field
        vals = {
            "o2m_ids": [fields.Command.link(i) for i in o2m_corecords.ids],
            "m2m_ids": [fields.Command.link(i) for i in m2m_corecords.ids],
        }
        # The diff should include only the IDs we want to link that are not already
        # linked
        self.assertEqual(
            record._get_write_diff_values(vals),
            # Odoo will update the commands to include the {"id": corecord.id} in them
            {
                "o2m_ids": [
                    (
                        fields.Command.LINK,
                        o2m_corecords[1].id,
                        {"id": o2m_corecords[1].id},
                    )
                ],
                "m2m_ids": [
                    (
                        fields.Command.LINK,
                        m2m_corecords[0].id,
                        {"id": m2m_corecords[0].id},
                    )
                ],
            },
        )
        record.write(vals)  # Do the real update => the diff should be empty now
        self.assertEqual(record._get_write_diff_values(vals), {})

    @mute_logger("bwd.test.model.log")
    def test_15_get_write_diff_values_x2many_command_clear(self):
        """Test ``_get_write_diff_values()`` on fields.Command.clear()

        ``_get_write_diff_values()`` returns only the subset of IDs that should be
        deleted/unlinked
        """
        record = self._create_records()
        # Create and assign 2 corecords to each X2M field
        record.o2m_ids = o2m_corecords = self._create_records(2)
        record.m2m_ids = m2m_corecords = self._create_records(2)
        # Set vals to clear each X2M field
        vals = {
            "o2m_ids": [fields.Command.clear()],
            "m2m_ids": [fields.Command.clear()],
        }
        self.assertEqual(
            record._get_write_diff_values(vals),
            # Odoo assigns command "delete" or "unlink" according to the field type
            # and its definition (not important for our purposes here)
            {
                "o2m_ids": [fields.Command.delete(i) for i in o2m_corecords.ids],
                "m2m_ids": [fields.Command.unlink(i) for i in m2m_corecords.ids],
            },
        )
        record.write(vals)  # Do the real update => the diff should be empty now
        self.assertEqual(record._get_write_diff_values(vals), {})

    @mute_logger("bwd.test.model.log")
    def test_16_get_write_diff_values_x2many_command_set(self):
        """Test ``_get_write_diff_values()`` on fields.Command.set()

        ``_get_write_diff_values()`` behavior depends on various cases
        """
        record = self._create_records()
        # Create 3 corecords for each X2M field
        o2m_corecords = self._create_records(3)
        m2m_corecords = self._create_records(3)

        # Case 1:
        # - X2M fields contain no corecords
        # - we want to assign them some corecords
        # => ``_get_write_diff_values()`` should return a ``fields.Command.link()``
        #    command for each corecord to add
        self.assertEqual(
            record._get_write_diff_values(
                {
                    "o2m_ids": [fields.Command.set(o2m_corecords.ids)],
                    "m2m_ids": [fields.Command.set(m2m_corecords.ids)],
                },
            ),
            # Odoo will update the commands to "link", and it will add the
            # {"id": corecord.id} in them
            {
                "o2m_ids": [
                    (fields.Command.LINK, i, {"id": i}) for i in o2m_corecords.ids
                ],
                "m2m_ids": [
                    (fields.Command.LINK, i, {"id": i}) for i in m2m_corecords.ids
                ],
            },
        )

        # Case 2:
        # - X2M fields contain some corecords
        # - we want to replace them with different corecords
        # => ``_get_write_diff_values()`` should return a
        #    ``fields.Command.[delete|unlink]()`` command for each corecord to remove,
        #    and a ``fields.Command.link()`` command for each corecord to add
        record.o2m_ids = o2m_corecords[:1]
        record.m2m_ids = m2m_corecords[:2]
        self.assertEqual(
            record._get_write_diff_values(
                {
                    "o2m_ids": [fields.Command.set(o2m_corecords[1:].ids)],
                    "m2m_ids": [fields.Command.set(m2m_corecords[2:].ids)],
                },
            ),
            # Odoo will update the commands to "unlink", "delete" and "link" (with the
            # {"id": corecord.id} in the "link" ones)
            {
                "o2m_ids": [
                    (fields.Command.DELETE, i, 0) for i in o2m_corecords[:1].ids
                ]
                + [(fields.Command.LINK, i, {"id": i}) for i in o2m_corecords[1:].ids],
                "m2m_ids": [
                    (fields.Command.UNLINK, i, 0) for i in m2m_corecords[:2].ids
                ]
                + [(fields.Command.LINK, i, {"id": i}) for i in m2m_corecords[2:].ids],
            },
        )

        # Case 3:
        # - X2M fields contain some corecords
        # - we want to reassign the same corecords
        # => ``_get_write_diff_values()`` should return nothing
        record.o2m_ids = o2m_corecords
        record.m2m_ids = m2m_corecords
        self.assertEqual(
            record._get_write_diff_values(
                {
                    "o2m_ids": [fields.Command.set(o2m_corecords.ids)],
                    "m2m_ids": [fields.Command.set(m2m_corecords.ids)],
                },
            ),
            {},
        )

        # Case 4:
        # - X2M fields contain some corecords
        # - we want to remove all corecords
        # => ``_get_write_diff_values()`` should return a
        #    ``fields.Command.[delete|unlink]()`` command for each linked corecord
        self.assertEqual(
            record._get_write_diff_values(
                {
                    "o2m_ids": [fields.Command.set([])],
                    "m2m_ids": [fields.Command.set([])],
                },
            ),
            # Odoo will update the commands to "unlink" and "delete"
            {
                "o2m_ids": [(fields.Command.DELETE, i, 0) for i in o2m_corecords.ids],
                "m2m_ids": [(fields.Command.UNLINK, i, 0) for i in m2m_corecords.ids],
            },
        )

    # pylint: disable=W0104
    def test_20_write_diff_computed_fields(self):
        """Checks cache behavior for computed fields when diff-writing their deps"""
        # Prepare the record, its fields values and the cache
        record = self._create_records()
        vals = {"length": 5, "width": 3, "height": 2}
        record.write(vals)
        fnames = ("perimeter", "area", "volume")
        for fname in fnames:
            with mute_logger("bwd.test.model.log"):
                record[fname]  # Dummy read: set fields in cache

        # Use ``write`` w/ the same values: Odoo will need to recompute the computed
        # fields values as soon as they're read
        record.write(vals)
        for fname in fnames:
            with self.assertLogs("bwd.test.model.log", level="WARNING"):
                record[fname]  # Dummy read: check the compute method is triggered

        # Use ``write_diff`` w/ the same values: Odoo won't need to recompute the
        # computed fields values
        record.write_diff(vals)
        for fname in fnames:
            with self.assertNoLogs("bwd.test.model.log", level="WARNING"):
                record[fname]  # Dummy read: check the compute method is not triggered
