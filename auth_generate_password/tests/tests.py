from odoo.tests.common import TransactionCase


class TestAuthGeneratePassword(TransactionCase):
    def setUp(self):
        super(TestAuthGeneratePassword, self).setUp()
        self.ir_model_data_obj = self.registry("ir.model.data")
        self.res_users_obj = self.registry("res.users")
        self.mail_mail_obj = self.registry("mail.mail")

    # Test Section
    def test_01_generate_set_and_send_password(self):
        self.ir_model_server_obj = self.registry("ir.mail_server")
        ir_model_server_ids = self.ir_model_server_obj.search([])
        self.ir_model_server_obj.unlink(ir_model_server_ids)
        mail_mail_qty_before = len(self.mail_mail_obj.search([]))
        self.extra_user = self.res_users_obj.create(
            {"name": "extra user", "login": "extra2", "email": "test@extra2.nl"}
        )
        mail_mail_qty_after = len(self.mail_mail_obj.search([]))
        self.assertEquals(
            mail_mail_qty_before + 1,
            mail_mail_qty_after,
            "Generate password for 1 user must send an email !",
        )
        mail_id = self.extra_user.generate_set_and_send_password()
        self.assertNotEqual(mail_id, False)
