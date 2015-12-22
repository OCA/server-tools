# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: nhomar@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):
    def test_01_pos_basic_order(self):
        self.phantom_js(
            "/", "openerp.Tour.run('test_instance_introspection', 'test')",
            "openerp.Tour.tours.test_instance_introspection", login="admin")

