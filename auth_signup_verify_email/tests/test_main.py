# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common, HttpCase


@common.at_install(False)
@common.post_install(True)
class TestUi(HttpCase):

    def test_10_register_with_email(self):
        # wait till page loaded and then click and wait again
        code = """
            setTimeout(function () {
            $("#login").val("test@example.com");
            $("#name").val("John Snow");
            $("form").submit();
            console.log("ok");
            });
        """
        self.phantom_js('/web/login', code)
