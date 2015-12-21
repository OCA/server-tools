# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ABF OSIELL (<http://osiell.com>).
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

from openerp import models, fields


class AuditlogLog(models.Model):
    _name = 'auditlog.log'
    _description = "Auditlog - Log"
    _order = "create_date desc"

    name = fields.Char("Resource Name", size=64)
    model_id = fields.Many2one(
        'ir.model', string=u"Model")
    res_id = fields.Integer(u"Resource ID")
    user_id = fields.Many2one(
        'res.users', string=u"User")
    method = fields.Char(u"Method", size=64)
    line_ids = fields.One2many(
        'auditlog.log.line', 'log_id', string=u"Fields updated")
    http_session_id = fields.Many2one(
        'auditlog.http.session', string=u"Session")
    http_request_id = fields.Many2one(
        'auditlog.http.request', string=u"HTTP Request")


class AuditlogLogLine(models.Model):
    _name = 'auditlog.log.line'
    _description = "Auditlog - Log details (fields updated)"

    field_id = fields.Many2one(
        'ir.model.fields', ondelete='cascade', string=u"Field", required=True)
    log_id = fields.Many2one(
        'auditlog.log', string=u"Log", ondelete='cascade')
    old_value = fields.Text(u"Old Value")
    new_value = fields.Text(u"New Value")
    old_value_text = fields.Text(u"Old value Text")
    new_value_text = fields.Text(u"New value Text")
    field_name = fields.Char(u"Technical name", related='field_id.name')
    field_description = fields.Char(
        u"Description", related='field_id.field_description')
