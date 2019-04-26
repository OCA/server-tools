# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring,invalid-name
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    ldap_id = fields.Many2one(
        comodel_name='res.company.ldap',
        help="Link to the ldap configuration, from which user was imported.\n"
             "Clear this field to keep user active, even when removed from"
             " ldap server.")
    last_synchronization = fields.Datetime(
        readonly=True,
        help="Show when last synchronized with ldap server.\n"
             " Can also be used to de-activate users on longer in ldap.")
