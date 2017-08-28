# -*- coding: utf-8 -*-
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from openerp.osv import orm, fields


class ResUser(orm.Model):
    _inherit = 'res.users'
    _columns = {
        'readonly_user': fields.boolean(
            "Read only user",
            help="Set this to prevent this user to modify any data")
    }
