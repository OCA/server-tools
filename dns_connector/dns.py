# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Liu Lixia, Augustin Cisterne-Kaas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class DNSBackend(models.Model):
    _name = 'dns.backend'
    _inherit = 'connector.backend'
    _backend_type = 'dns'

    def select_version(self):
        return []

    login = fields.Char('Login', help='Provider\'s login.', required=True)
    password = fields.Char('Password', help='Provider\'s password.', required=True)
    state = fields.Selection(
        [('draft', 'Not confirmed'), ('done', 'Confirmed'),
         ('exception', 'Exception')], 'State', default="draft",
        help='"Confirmed" when the domain has been succesfully created.')
    version = fields.Selection(
        select_version, string='Service Provider', help='DNS service provider', required=True)

    @api.multi
    def name_get(self):
        res = []
        for backend in self:
            res.append((backend.id, '%s (%s)' % (backend.name, backend.login)))
        return res


class DNSDomain(models.Model):
    _name = 'dns.domain'
    _inherit = 'dns.binding'

    name = fields.Char('Name', required=True, help='Domain name without "www",such as"dnspod.cn"')
    record_ids = fields.One2many('dns.record', 'domain_id', String='Subdomains')


class DNSRecord(models.Model):
    _name = 'dns.record'
    _inherit = 'dns.binding'

    def line_select_version(self):
        res = []
        return res

    def type_select_version(self):
        return []

    name = fields.Char('Sub domain', help="host record,such as 'www'", required=True)
    domain_id = fields.Many2one(
        'dns.domain', string="Domain", domain="[('state','=','done')]",
        help="Domain which has already confirmed")
    type = fields.Selection(type_select_version, string='Record Type')
    line = fields.Selection(line_select_version, string='Record Line')
    value = fields.Text('Value', help="such as IP:200.200.200.200", required=True)
    mx_priority = fields.Integer(string='MX priority', help="scope:1-20", default=1)
    ttl = fields.Integer('TTL', default=600, help="scope:1-604800", required=True)
    backend_id = fields.Many2one('dns.backend', related='domain_id.backend_id', store=True)
