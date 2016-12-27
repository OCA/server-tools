# -*- coding: utf-8 -*-
# © 2012 Therp BV (<http://therp.nl>)
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

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if 'ldap_id' in vals:
            ldap = self.env['res.company.ldap'].browse(vals['ldap_id'])
            vals['users_created'] = ldap.action_populate()
        return super(CompanyLDAPPopulateWizard, self).create(vals)
