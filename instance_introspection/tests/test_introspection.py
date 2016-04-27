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
    def test_01_instance_introspection(self):
        '''Just load the introspection of instance.
        '''
        self.phantom_js(
            "/web", "openerp.Tour.run('test_instance_introspection', 'test')",
            "openerp.Tour.tours.test_instance_introspection", login="admin")

    def test_02_pyinfo(self):
        '''PyInfo page being loaded the introspection of instance.
        '''
        self.phantom_js(
            "/web", "openerp.Tour.run('test_pyinfo', 'test')",
            "openerp.Tour.tours.test_pyinfo", login="admin")

    def test_03_pyinfo(self):
        '''Instrospection, just download a json
        '''
        self.phantom_js(
            "/web", "openerp.Tour.run('test_pyinfo_json', 'test')",
            "openerp.Tour.tours.test_pyinfo_json", login="admin")

    def test_04_pyinfo(self):
        '''Instrospection, just download a json
        '''
        self.phantom_js(
            "/web", "openerp.Tour.run('test_pyinfo_json', 'test')",
            "openerp.Tour.tours.test_pyinfo_json", login="admin")
