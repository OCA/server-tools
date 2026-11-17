# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import AuditLogRuleCommon


class TestCreateWithPendingDirtyRecords(AuditLogRuleCommon):
    """Creating a record under a "full" log rule must not break when
    another record still has pending (unflushed) field updates.

    Observed on Odoo 19 when creating a sale order while its delivery
    order was in flight: the create failed with "Could not find all
    values of stock.picking(...) to flush them". The auditlog snapshot
    read through a temporary cache while the ORM still saw the dirty
    marks, and the flush triggered by the read could not find the
    values.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.groups_model_id = cls.env.ref("base.model_res_groups").id
        cls.groups_rule = cls.create_rule(
            {
                "name": "testrule for groups",
                "model_id": cls.groups_model_id,
                "log_create": True,
                "log_type": "full",
            }
        )

    def test_create_with_pending_field_update(self):
        """A full-logged create succeeds while another record is dirty."""
        self.groups_rule.set_to_confirmed()
        # Bind the dirty-marks view of the sudo environment the log
        # snapshot will use; this mimics sudo work in flight during the
        # create, like a delivery order updated while creating an order.
        sudoed = self.env["res.groups"].with_context(auditlog_disabled_read=True).sudo()
        sudoed.flush_model()
        group = self.env["res.groups"].create({"name": "testgroup"})
        # Leave an update pending on a field the create below does not
        # touch; regular writes would flush it right away
        sudoed._fields["sequence"].write(sudoed.browse(group.id), 5)
        # The logged create used to crash inside the temporary read cache
        new_group = self.env["res.groups"].create({"name": "new group"})
        self.assertEqual(
            self.env["auditlog.log"].search_count(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", new_group.id),
                ]
            ),
            1,
        )
