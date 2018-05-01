# Copyright 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2017 Eficent <http://www.eficent.com>
# Copyright 2018 Hai Dinh <haidd.uit@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FetchmailServer(models.Model):

    _inherit = 'fetchmail.server'
    error_notice_template_id = fields.Many2one(
        'mail.template', string="Error notice template",
        help="Set here the template to use to send notice to sender when "
             "errors occur while fetching email")
