# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    last_ldap_login = fields.Char(string=u"Ldap login", readonly=True)
