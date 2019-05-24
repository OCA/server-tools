# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring,invalid-name,protected-access
from odoo import api, models


class ResCompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    @api.model
    def create(self, vals):
        """Make sure vals contains a company_id.

        The link in standard Odoo between company and ldap server settings
        lacks any logic. But the company must still be filled, so we default
        it to the company of the user.

        It might be usefull in a multi-company situation to enable imported
        users to one or more, or all companies. As yet we do nothing specific
        to support this.
        """
        if not 'company' in vals:  # missing _id on field name is from Odoo.
            vals['company'] = self.env.user.company_id.id
        return super(ResCompanyLDAP, self).create(vals)
