from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestBaseMultiImage(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create a non-admin user
        self.base_user = new_test_user(
            self.env,
            name="Base User",
            login="base_user",
            groups="base.group_user",
        )

        # Create a base_multi_image.image record
        self.image_record = self.env["base_multi_image.image"].create(
            {
                "name": "Test Image",
                "owner_model": "res.partner",
                "owner_id": self.env["res.partner"]
                .create(
                    {
                        "name": "Partner",
                    }
                )
                .id,
            }
        )

    def test_selection_owner_ref_id_access(self):
        """
        Ensure _selection_owner_ref_id works for non-admin users.
        """
        base_user_env = self.env(user=self.base_user.id)
        image = base_user_env["base_multi_image.image"].browse(self.image_record.id)

        # It should not raise an AccessError
        selection = image._selection_owner_ref_id()

        self.assertIsInstance(selection, list)
        self.assertTrue(len(selection) > 0)
