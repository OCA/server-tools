# Copyright 2012 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models, fields, api


class CompanyLDAPPopulateWizard(models.TransientModel):
    _name = 'res.company.ldap.populate_wizard'
    _description = 'Populate users from LDAP'

    name = fields.Char('Name', size=16)
    ldap_id = fields.Many2one(
        'res.company.ldap',
        'LDAP Configuration'
    )
    users_created = fields.Integer(
        'Number of users created',
        readonly=True
    )
    users_deactivated = fields.Integer(
        'Number of users deactivated',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        ResCompanyLDAPObj = self.env['res.company.ldap']
        for vals in vals_list:
            if 'ldap_id' in vals:
                ldap = ResCompanyLDAPObj.browse(vals['ldap_id'])
                vals['users_created'], vals['users_deactivated'] =\
                    ldap.action_populate()
        return super().create(vals_list)
