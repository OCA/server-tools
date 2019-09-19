# -*- coding: utf-8 -*-
# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MailMessage(models.Model):
    _name = "mail.message"
    _inherit = ["mail.message", "autovacuum.mixin"]
