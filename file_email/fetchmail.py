# -*- coding: utf-8 -*-
###############################################################################
#
#   file_email for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api


class fetchmail_server(models.Model):
    _inherit = 'fetchmail.server'

    @api.model
    def get_file_type(self):
        return []

    @api.model
    def _get_file_type(self):
        return self.get_file_type()

    def company_default_get(self):
        company_id = (self.env['res.company'].
                      _company_default_get('fetchmail.server'))
        return self.env['res.company'].browse(company_id)

    file_type = fields.Selection(
        selection='_get_file_type',
        help='The file type will show some special option')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=company_default_get
        )  # Why this field do not exist by default?
    attachment_metadata_condition_ids = fields.One2many(
        'ir.attachment.metadata.condition', 'server_id', string='Attachment')

    @api.one
    def get_context_for_server(self):
        if self._context is None:
            ctx = {}
        else:
            ctx = self._context.copy()
        ctx['default_attachment_metadata_vals'] = {}
        ctx['default_company_id'] = self.company_id.id
        ctx['default_fetchmail_server_id'] = self.id
        return ctx

    @api.multi
    def fetch_mail(self):
        for server in self:
            super(fetchmail_server, server).fetch_mail()
        return True
