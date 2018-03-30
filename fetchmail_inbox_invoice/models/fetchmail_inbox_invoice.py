# coding: utf-8
# Copyright (C) 2014 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class FetchmailInboxInvoice(models.Model):
    _inherit = 'fetchmail.inbox'
    _name = 'fetchmail.inbox.invoice'
    _table = 'fetchmail_inbox'
    _description = 'Fetchmail inbox for invoices'
