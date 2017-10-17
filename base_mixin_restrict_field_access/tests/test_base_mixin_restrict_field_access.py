# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models
from openerp.osv import expression
from openerp.tests.common import TransactionCase


class TestBaseMixinRestrictFieldAccess(TransactionCase):
    def test_base_mixin_restrict_field_access(self):
        # inherit from our mixin. Here we want to restrict access to
        # all fields when the partner has a credit limit of less than 42
        # and the current user is not an admin
        class ResPartner(models.Model):
            _inherit = ['restrict.field.access.mixin', 'res.partner']
            _name = 'res.partner'

            # implement a record specific whitelist: credit limit is only
            # visible for normal users if it's below 42
            @api.multi
            def _restrict_field_access_is_field_accessible(
                    self, field_name, action='read'
            ):
                result = super(ResPartner, self)\
                    ._restrict_field_access_is_field_accessible(
                        field_name, action=action
                    )
                if not self._restrict_field_access_get_is_suspended() and\
                   not self.env.user.has_group('base.group_system') and\
                   field_name not in models.MAGIC_COLUMNS and self:
                    result = all(
                        this.sudo().credit_limit < 42 for this in self
                    )
                return result

            # and as the documentation says, we need to add a domain to enforce
            # this
            def _restrict_field_access_inject_restrict_field_access_domain(
                    self, domain
            ):
                domain[:] = expression.AND([
                    expression.normalize_domain(domain),
                    [('credit_limit', '<', 42)]
                ])
        # call base-suspend_security's register hook
        self.env['ir.rule']._register_hook()

        # setup the model
        res_partner = ResPartner._build_model(self.registry, self.cr).browse(
            self.cr, self.uid, [], context={})
        res_partner._prepare_setup()
        res_partner._setup_base(False)
        res_partner._setup_fields()
        res_partner._setup_complete()

        # run tests as nonprivileged user
        partner_model = res_partner.sudo(self.env.ref('base.user_demo').id)
        partner = partner_model.create({
            'name': 'testpartner',
        })
        self.assertFalse(partner.restrict_field_access)
        partner.sudo().write({'credit_limit': 42})
        partner.invalidate_cache()
        self.assertTrue(partner.restrict_field_access)
        self.assertFalse(partner.credit_limit)
        self.assertTrue(partner.sudo().credit_limit)
        # not searching for some restricted field should yield the partner
        self.assertIn(partner, partner_model.search([]))
        # but searching for it should not
        self.assertNotIn(
            partner,
            partner_model.search([
                ('credit_limit', '=', 42)
            ])
        )
        # when we copy stuff, restricted fields should be copied, but still
        # be inaccessible
        new_partner = partner.copy()
        self.assertFalse(new_partner.credit_limit)
        self.assertTrue(new_partner.sudo().credit_limit)
        # check that our field injection works
        fields_view_get = partner.fields_view_get()
        self.assertIn('restrict_field_access', fields_view_get['arch'])
        # check that the export does null offending values
        export = partner._BaseModel__export_rows([['id'], ['credit_limit']])
        self.assertEqual(export[0][1], '0.0')
        # but that it does export the value when it's fine
        partner.sudo().write({'credit_limit': 41})
        partner.invalidate_cache()
        export = partner._BaseModel__export_rows([['id'], ['credit_limit']])
        self.assertEqual(export[0][1], '41.0')
        # read_group should behave like search: restrict to records with our
        # field accessible if a restricted field is requested, unrestricted
        # otherwise
        data = partner_model.read_group(
            [], [], ['user_id']
        )
        self.assertEqual(sum(d['credit_limit'] for d in data), 41)
        # but users with permissions should see the sum for all records
        data = partner_model.sudo().read_group(
            [], [], ['user_id']
        )
        self.assertEqual(
            sum(d['credit_limit'] for d in data),
            sum(partner_model.sudo().search([]).mapped('credit_limit'))
        )
