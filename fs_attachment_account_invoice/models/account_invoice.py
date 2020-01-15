# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, SUPERUSER_ID, exceptions, _
from datetime import datetime

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('name', 'partner_id', 'journal_id', 'company_id')
    def _compute_fs_rel_path(self):
        for invoice in self:
            if invoice.date_invoice:
                invoice.filesystem_storage_rel_path = "%s/%s/%s/%s" % (
                    invoice.journal_id.display_name,
                    invoice.date_invoice.strftime("%Y"),
                    invoice.date_invoice.strftime("%B"),
                    invoice.name
                )
            else:
                today = datetime.now()
                invoice.filesystem_storage_rel_path = "%s/%s/%s/%s" % (
                    invoice.journal_id.display_name,
                    today.strftime("%Y"),
                    today.strftime("%B"),
                    invoice.name
                )

    @api.multi
    @api.depends('filesystem_storage_rel_path', 'company_id')
    def _compute_fs_uri(self):
        for invoice in self:
            invoice.filesystem_uri = "%s/%s" % (invoice.company_id.uri_storage_path, invoice.filesystem_storage_rel_path)

    def _set_fs_rel_path(self):
        pass

    filesystem_storage_rel_path = fields.Char('Filesystem Rel Path', compute='_compute_fs_rel_path',
                                              inverse='_set_fs_rel_path', store=True, index=True)
    filesystem_uri = fields.Char('Directory URI', compute='_compute_fs_uri', store=True)
