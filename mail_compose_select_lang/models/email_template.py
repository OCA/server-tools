# -*- encoding: utf-8 -*-
##############################################################################
# Copyright 2015 Pedro M. Baeza
# For license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class EmailTemplate(models.Model):
    _inherit = 'email.template'

    @api.model
    def get_email_template_batch(self, template_id=False, res_ids=None):
        if template_id and res_ids and self.env.context.get('force_lang'):
            template = self.env['email.template'].with_context(
                lang=self.env.context['force_lang']).browse(template_id)
            return dict.fromkeys(res_ids, template)
        else:
            return super(EmailTemplate, self).get_email_template_batch(
                template_id=template_id, res_ids=res_ids)
