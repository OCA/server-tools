# -*- coding: utf-8 -*-
# © 2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models, osv


class ResCompanyA(models.Model):
    _inherit = 'res.company'

    prefix_a_name = fields.Char()
    prefix_a_integer = fields.Integer()
    prefix_a_partner_id = fields.Many2one(comodel_name='res.partner')


class ResCompanyB(models.Model):
    _inherit = 'res.company'

    _columns = {
        'prefix_b_name': osv.fields.char('name'),
        'prefix_b_integer': osv.fields.integer('int'),
        'prefix_b_partner_id': osv.fields.many2one('res.partner'),
    }


class MyConfigA(models.TransientModel):
    _name = 'a.config.settings'
    _inherit = ['res.config.settings', 'abstract.config.settings']
    _prefix = 'prefix_a_'
    _companyObject = ResCompanyA


class MyConfigB(models.TransientModel):
    _name = 'b.config.settings'
    _inherit = ['res.config.settings', 'abstract.config.settings']
    _prefix = 'prefix_b_'
    _companyObject = ResCompanyB
