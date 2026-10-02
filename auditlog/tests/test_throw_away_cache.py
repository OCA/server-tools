# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.auditlog.models.auditlog_rule import ThrowAwayCache

from .common import AuditLogRuleCommon


class TestThrowAwayCache(AuditLogRuleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_model_id = cls.env.ref("base.model_res_partner_category").id
        cls.category_rule = cls.create_rule(
            {
                "name": "testrule for partner categories",
                "model_id": cls.category_model_id,
                "log_read": False,
                "log_create": True,
                "log_write": False,
                "log_unlink": False,
                "log_type": "full",
            }
        )

    def test_field_dirty_memo(self):
        """The environments resolve the field_dirty currently in place.

        `Environment._field_dirty` is a `functools.cached_property`, so the
        environments that already accessed it have to be reset when the
        container is swapped, and again when it is restored.
        """
        transaction = self.env.transaction
        original = self.env._field_dirty
        with ThrowAwayCache(self.env):
            self.assertIsNot(self.env._field_dirty, original)
            self.assertIs(self.env._field_dirty, transaction.field_dirty)
        self.assertIs(self.env._field_dirty, original)
        self.assertIs(self.env._field_dirty, transaction.field_dirty)

    def test_create_with_pending_writes(self):
        """Log a creation while another model has unflushed values.

        Taking the snapshot of the new record reads all of its fields, and
        reading a relational field runs a query that flushes the model on the
        other side of the relation. The values to flush must not be looked up
        in the disposable cache, as they only live in the real one.
        """
        self.category_rule.set_to_confirmed()
        other_category = self.env["res.partner.category"].create(
            {"name": "testcategory already stored"}
        )
        self.env.flush_all()

        # Leave a value in the cache that is not written to the database yet
        other_category.name = "testcategory not flushed yet"
        field = self.env["res.partner.category"]._fields["name"]
        self.assertIn(
            other_category.id, self.env.transaction.field_dirty.get(field, ())
        )

        # Reading the relational fields of the new record runs queries that
        # flush the models they read from
        category = self.env["res.partner.category"].create(
            {"name": "testcategory with pending writes"}
        )

        self.assertEqual(
            self.env["auditlog.log"].search_count(
                [
                    ("model_id", "=", self.category_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", category.id),
                ]
            ),
            1,
        )
        self.assertEqual(other_category.name, "testcategory not flushed yet")
