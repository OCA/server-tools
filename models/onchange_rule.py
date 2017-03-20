# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
from lxml import etree
from collections import defaultdict

from odoo.osv import orm
from odoo import api, fields, models
# from odoo.exceptions import UserError


class OnchangeRule(models.Model):
    _name = "onchange.rule"

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get()

    name = fields.Char(required=True)
    active = fields.Boolean(
        default=True,
        help="The active field allows you to make your record "
             "without effect but without remove it.")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', index=1,
        default=_default_company)
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True,
        help="")
    field_id = fields.Many2one(
        comodel_name='ir.model.fields', string='Onchange Field',
        domain="[('model_id', '=', model_id)]", required=True)
    implied_model = fields.Char(
        string='Implied Model',
        related='field_id.relation',
        help="")
    readonly = fields.Boolean(
        help="If checked ensure than record can't be updated by user "
             "(only by inserted data)")
    sequence = fields.Integer()
    line_ids = fields.One2many(
        comodel_name='onchange.rule.line', inverse_name='onchange_rule_id',
        string='Onchange Rule Lines')

    @api.onchange('model_id')
    def _onchange_field(self):
        self.field_id = False

    @api.model
    def _customize_view_according_to_setting_rule(
            self, res, view_type, src_model):
        if view_type == 'form':
            rules = self._get_rules_from_model(src_model._name)
            if rules:
                doc = etree.XML(res['arch'])
                params, readonly = (self.env['onchange.rule']
                                    ._get_config_from_model(
                                        src_model._name, rules))
                fields_def = src_model.fields_get(
                    allfields=None, attributes=None)
                print 'params, reado', params, readonly
                for field in params.keys():
                    for param in params[field]:
                        self._update_nodes_from_rule(
                            doc, fields_def, field, 'on_change', 1)
                for field in readonly:
                    self._update_nodes_from_rule(
                        doc, fields_def, field, 'attrs', {'readonly': 1})
                res['arch'] = etree.tostring(doc, pretty_print=True)
        return res

    @api.model
    def _get_rules_from_model(self, model_name):
        model = self.env['ir.model'].search([('model', '=', model_name)])
        return self.env['onchange.rule'].search(
            [('model_id', '=', model.id)])

    @api.model
    def _get_config_from_model(self, model_name, rules):
        params = defaultdict(list)
        readonly, configs = [], {}
        for rule in rules:
            if rule.config:
                config = ast.literal_eval(rule.config)
                for __, conf in config.items():
                    for field, params in conf.items():
                        if params.get('readonly'):
                            readonly.append(field)
                configs[rule.field_id.name] = config
        return (configs, readonly)

    @api.model
    def _update_nodes_from_rule(self, doc, fields_def, field, tag, attrs):
        for path in ("//field[@name='%s']", "//label[@for='%s']"):
            node = doc.xpath(path % field)
            if node:
                for current_node in node:
                    current_node.set(tag, str(attrs))
                    orm.setup_modifiers(current_node, fields_def[field])
                    print "         NODE  ", current_node.values()

    @api.model
    def _update_onchange_values(self, model_name, values, res, field_name):
        rules = self._get_rules_from_model(model_name)
        if rules:
            configs, _ = self._get_config_from_model(self._name, rules)
            if field_name in configs.keys():
                if values[field_name] in configs[field_name].keys():
                    field_value = values[field_name]
                    param_field = configs[field_name][field_value]
                    for field in param_field:
                        res['value'][field] = param_field[field]['value']
        return res
