# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from openerp import models


class TestBaseMixinRestrictFieldAccess(TransactionCase):
    def test_base_mixin_restrict_field_access(self):
        # inherit from our mixin
        class ResPartner(models.Model):
            _inherit = ['restrict.field.access.mixin', 'res.partner']
            _name = 'res.partner'

        # setup the model
        res_partner = ResPartner._build_model(self.registry, self.cr).browse(
            self.cr, self.uid, [], context={})
        res_partner._prepare_setup()
        res_partner._setup_base(False)
        res_partner._setup_fields()
        res_partner._setup_complete()
        # run tests as nonprivileged user
        partner = res_partner.sudo(self.env.ref('base.user_demo').id).create({
            'name': 'testpartner',
        })
        partner.copy()
        partner.write({
            'name': 'testpartner2',
        })
        partner.search([])
        self.assertTrue(partner.restrict_field_access)
        partner.fields_view_get()
        # TODO: a lot more tests
