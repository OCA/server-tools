# Copyright 2017-2018 Therp BV <http://therp.nl>
# Copyright 2020 Hunki Enterprises BV <https://hunki-enterprises.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from mock import patch

from odoo.tests.common import TransactionCase, tagged

from ..models.import_odoo_database import ImportContext, field_context


class TestBaseImportOdoo(TransactionCase):
    def setUp(self):
        super(TestBaseImportOdoo, self).setUp()
        # if our tests run with an accounting scheme, it will fail on accounts
        # to fix this, if the account model exists, we create mappings for it
        if "account.account" in self.env.registry:
            self.env.ref("base_import_odoo.demodb").write(
                {
                    "import_field_mappings": [
                        (
                            0,
                            False,
                            {
                                "mapping_type": "fixed",
                                "model_id": self.env.ref(
                                    "account.model_account_account"
                                ).id,
                                "local_id": account.id,
                                "remote_id": account.id,
                            },
                        )
                        for account in self.env["account.account"].search([])
                    ],
                }
            )
        # not sure why this is needed... but odoo init of demo data does not work properly.
        mapping_attachment = self.env.ref("base_import_odoo.mapping_attachment")
        mapping_attachment.id_field_id = self.env.ref("base.field_ir_attachment__res_id")

    @tagged("post_install", "-at_install")
    @patch(
        "odoorpc.ODOO.__init__",
        side_effect=lambda self, *args, **kwargs: None,
    )
    @patch("odoorpc.ODOO.login", side_effect=lambda *args: None)
    def test_base_import_odoo(self, mock_client, mock_client_login):
        # the mocked functions simply search/read in the current database
        # the effect then should be that the models in question are duplicated,
        # we just need to try not to be confused by the fact that local and
        # remote ids are the same
        def _mock_execute(model, method, *args):
            if method == "read":
                return self.env[model].browse(args[0]).read(args[1])
            if method == "search":
                return self.env[model].search(args[0]).ids
            if method == "fields_get":
                return self.env[model].fields_get()

        group_count = self.env["res.groups"].search([], count=True)
        user_count = self.env["res.users"].search([], count=True)
        run = 1
        for _dummy in range(2):
            # we run this two times to enter the code path where xmlids exist
            self.env.ref("base_import_odoo.demodb").write({"password": "admin"})
            with patch("odoorpc.ODOO.execute", side_effect=_mock_execute):
                self.env.ref("base_import_odoo.demodb")._run_import()
            # here the actual test begins - check that we created new
            # objects, check xmlids, check values, check if dummies are
            # cleaned up/replaced
            imported_user = self.env.ref(self._get_xmlid("base.user_demo"))
            user = self.env.ref("base.user_demo")
            self.assertNotEqual(imported_user, user)
            # check that the imported scalars are equal
            fields = ["name", "email", "signature", "active"]
            (imported_user + user).read(fields)
            self.assertEqual(
                self._get_cache(self._get_xmlid("base.user_demo"), fields),
                self._get_cache("base.user_demo", fields),
            )
            # check that links are correctly mapped
            self.assertEqual(
                imported_user.partner_id,
                self.env.ref(self._get_xmlid("base.partner_demo")),
            )
            # no new groups because they should be mapped by name
            self.assertEqual(group_count, self.env["res.groups"].search([], count=True))
            # all users save for root should be duplicated for every run
            self.assertEqual(
                self.env["res.users"].search([], count=True),
                user_count + (user_count - 1) * run,
            )
            # check that there's a new attachment
            attachment = self.env.ref("base_import_odoo.attachment_demo")
            imported_attachment = self.env["ir.attachment"].search(
                [("res_model", "=", "res.users"), ("res_id", "=", imported_user.id)]
            )
            self.assertTrue(attachment)
            self.assertEqual(attachment.datas, imported_attachment.datas)
            self.assertNotEqual(attachment, imported_attachment)
            run += 1
        demodb = self.env.ref("base_import_odoo.demodb")
        for line in demodb.import_line_ids:
            self.assertIn(line.model_id.model, demodb.status_html)
        demodb.action_import()
        self.assertTrue(demodb.cronjob_id)
        demodb.cronjob_id.write({"active": False})
        demodb.action_import()
        self.assertTrue(demodb.cronjob_id.active)
        self.assertFalse(demodb.cronjob_running)
        # in our setting we won't get dummies, so we test this manually
        import_context = ImportContext(
            None,
            self.env.ref("base_import_odoo.model_partner"),
            [],
            {},
            {},
            [],
            {},
            field_context(None, None, None),
        )
        dummy_id = demodb._run_import_create_dummy(
            import_context,
            self.env["res.partner"],
            {"id": 424242},
            forcecreate=True,
        )
        self.assertTrue(self.env["res.partner"].browse(dummy_id).exists())

    def _get_xmlid(self, remote_xmlid):
        remote_obj = self.env.ref(remote_xmlid)
        return "__base_import_odoo__.%d-%s-%s" % (
            self.env.ref("base_import_odoo.demodb").id,
            remote_obj._name.replace(".", "_"),
            remote_obj.id,
        )

    def _get_cache(self, xmlid, fields):
        record = self.env.ref(xmlid)
        return {
            field_name: record._cache[field_name]
            for field_name in record._fields
            if field_name in fields
        }
