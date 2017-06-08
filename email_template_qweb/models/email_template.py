# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, tools, models


class EmailTemplate(models.Model):
    _inherit = 'email.template'

    body_type = fields.Selection(
        [('jinja2', 'Jinja2'), ('qweb', 'QWeb')], 'Body templating engine',
        default='jinja2', required=True)
    body_view_id = fields.Many2one(
        'ir.ui.view', 'Body view', domain=[('type', '=', 'qweb')])
    body_view_arch = fields.Text(related=['body_view_id', 'arch'])

    @api.model
    def generate_email_batch(self, template_id, res_ids, fields=None):
        result = super(EmailTemplate, self).generate_email_batch(
            template_id, res_ids, fields=fields)
        this = self.browse(template_id)
        for record_id, this in self.get_email_template_batch(
            template_id, res_ids
        ).iteritems():
            if this.body_type == 'qweb' and\
                    (not fields or 'body_html' in fields):
                for record in self.env[this.model].browse(record_id):
                    result[record_id]['body_html'] = self.render_post_process(
                        this.body_view_id.render({
                            'object': record,
                            'email_template': this,
                        })
                    )
                    result[record_id]['body'] = tools.html_sanitize(
                        result[record_id]['body_html']
                    )
        return result
