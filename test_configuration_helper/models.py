# © 2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    prefix_a_name = fields.Char()
    prefix_a_integer = fields.Integer()
    prefix_a_partner_id = fields.Many2one(comodel_name='res.partner')


class MyConfigA(models.TransientModel):

    _inherit = ['res.config.settings', 'abstract.config.settings']
    _prefix = 'prefix_a_'
    _companyObject = ResCompany
