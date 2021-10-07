# Copyright 2017 Lorenzo Battistini - Agile Business Group
# Copyright 2021 Lorenzo Battistini - TAKOBI
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from odoo import fields, models, api


class ResUser(models.Model):
    _inherit = 'res.users'

    readonly_user = fields.Boolean(
        string="Read only user",
        help="Set this to prevent this user to modify any data")
