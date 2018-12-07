# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import datetime
import dateutil.relativedelta as relativedelta
from odoo import api, models, tools
from odoo.tools.safe_eval import safe_eval
from werkzeug import urls
from jinja2.sandbox import SandboxedEnvironment
_logger = logging.getLogger(__name__)
jinja2_template_env = SandboxedEnvironment(
    variable_start_string="${",
    variable_end_string="}",
    trim_blocks=True,               # do not output newline after blocks
    autoescape=True,                # XML/HTML automatic escaping
)
jinja2_template_env.globals.update({
    'str': str,
    'quote': urls.url_quote,
    'datetime': datetime,
    'len': len,
    'abs': abs,
    'min': min,
    'max': max,
    'sum': sum,
    'round': round,
    'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a, **kw)
})


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    def create(self, vals):
        res = super(Attachment, self).create(vals)
        res.create_metadata()
        return res

    @api.multi
    def create_metadata(self):
        """Use sequence to obtain the rule with high priority"""
        sync_rule_obj = self.env['ir.attachment.sync.rule']
        for attachment in self:
            # check if res_model is in the define rules.
            all_matching_rules = sync_rule_obj.search([
                ('source_model.object', '=', attachment.res_model)
            ], order='sequence asc')
            selected_matching_rules = []
            for rule in all_matching_rules:
                if rule.domain:
                    domain = safe_eval(rule.domain)
                    domain.append(('id', '=', attachment.res_id))
                    if not self.env[attachment.res_model].search(domain):
                        continue
                previous_rules_with_same_loc_and_lower_seq = [
                    previous_rule for previous_rule in selected_matching_rules
                    if previous_rule.sync_type == rule.sync_type
                    and previous_rule.sequence < rule.sequence
                ]
                if not previous_rules_with_same_loc_and_lower_seq:
                    selected_matching_rules.append(rule)
            for rule in selected_matching_rules:
                # Check if attachment already exists in the metas
                metadata_obj = self.env['ir.attachment.metadata']
                existing_metas = metadata_obj.search(
                    [('attachment_id', '=', attachment.id)])
                locations = existing_metas.mapped('location_id').ids
                if not existing_metas or rule.location_id.id not in \
                        locations:
                    # Gather vals from sync_rule
                    name = self.render_template(
                        rule.file_name_format,
                        rule.source_model.object,
                        attachment.res_id)
                    vals = {
                        'attachment_id': attachment.id,
                        'name': attachment.display_name,
                        'type': 'binary',
                        'task_id': rule.location_id.task_ids[0].id,
                        'file_type': 'export_external_location',
                    }
                    if name:
                        other_metas = metadata_obj.search([
                            ('res_id', '=', attachment.res_id),
                            ('location_id', '=', rule.location_id.id)
                        ])
                        if other_metas:
                            fname = "%s(%s)%s" % (
                                name, len(other_metas),
                                attachment.datas_fname[-4:]
                            )
                        else:
                            fname = name + attachment.datas_fname[-4:]
                        vals['datas_fname'] = fname
                    metadata_obj.create(vals)
        return True

    def render_template(self, template, model, res_id):
        template = jinja2_template_env.from_string(tools.ustr(template))
        user = self.env.user
        record = self.env[model].browse(res_id)

        variables = {
            'user': user
        }
        variables['object'] = record
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.error("Failed to render template %r using values %r" % (
                template, variables))
            render_result = u""
        if render_result == u"False":
            render_result = u""

        return render_result
