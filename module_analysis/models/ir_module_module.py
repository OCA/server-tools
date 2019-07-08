# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging
import os
import subprocess

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.modules.module import get_module_path

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    author_ids = fields.Many2many(
        string='Authors', comodel_name='ir.module.author', readonly=True,
        relation='ir_module_module_author_rel')

    module_type_id = fields.Many2one(
        string='Module Type', comodel_name='ir.module.type', readonly=True)

    python_lines_qty = fields.Integer(string='Python Lines', readonly=True)

    xml_lines_qty = fields.Integer(string='XML Lines', readonly=True)

    js_lines_qty = fields.Integer(string='JS Lines', readonly=True)

    css_lines_qty = fields.Integer(string='CSS Lines', readonly=True)

    @api.model
    def update_list(self):
        res = super(IrModuleModule, self).update_list()
        if self.env.context.get('analyze_installed_modules', False):
            self.search([('state', '=', 'installed')]).button_analyze_code()
        return res

    @api.multi
    def write(self, vals):
        res = super(IrModuleModule, self).write(vals)
        if vals.get('state', False) == 'installed':
            self.button_analyze_code()
        elif vals.get('state', False) == 'uninstalled'\
                and 'module_analysis' not in [x.name for x in self]:
            self.write({
                'author_ids': [6, 0, []],
                'module_type_id': False,
                'python_lines_qty': False,
                'xml_lines_qty': 0,
                'js_lines_qty': 0,
                'css_lines_qty': 0,
            })
        return res

    @api.multi
    def button_analyze_code(self):
        IrModuleAuthor = self.env['ir.module.author']
        IrModuleTypeRule = self.env['ir.module.type.rule']
        rules = IrModuleTypeRule.search([])

        exclude_dir = "lib,description,tests,demo"
        include_lang = self._get_analyzed_languages()

        for module in self:
            _logger.info("Analyzing Code for module %s" % (module.name))

            # Update Authors, based on manifest key
            authors = []
            if module.author and module.author[0] == '[':
                author_txt_list = safe_eval(module.author)
            else:
                author_txt_list = module.author.split(',')

            author_txt_list = [x.strip() for x in author_txt_list]
            author_txt_list = [x for x in author_txt_list if x]
            for author_txt in author_txt_list:
                authors.append(IrModuleAuthor._get_or_create(author_txt))

            author_ids = [x.id for x in authors]
            module.author_ids = author_ids

            # Update Module Type, based on rules
            module_type_id = rules._get_module_type_id_from_module(module)
            module.module_type_id = module_type_id

            # Get Path of module folder and parse the code
            path = get_module_path(module.name)

            try:
                command = [
                    'cloc',
                    '--exclude-dir=%s' % (exclude_dir),
                    '--skip-uniqueness',
                    '--include-lang=%s' % (include_lang),
                    '--not-match-f="__openerp__.py|__manifest__.py"',
                    '--json',
                    os.path.join(path)]
                temp = subprocess.Popen(command, stdout=subprocess.PIPE)
                bytes_output = temp.communicate()
                output = bytes_output[0].decode("utf-8").replace('\n', '')
                json_res = json.loads(output)
                values = self._prepare_values_from_json(json_res)
                module.write(values)

            except Exception as e:
                _logger.warning(
                    'Failed to execute the cloc command on module %s\n'
                    'Exception occured: %s' % (
                        module.name, e))

    @api.model
    def _get_analyzed_languages(self):
        "Overload the function to add extra languages to analyze"
        return "Python,XML,JavaScript,CSS"

    @api.model
    def _prepare_values_from_json(self, json_value):
        return {
            'python_lines_qty': json_value.get('Python', {}).get('code', 0),
            'xml_lines_qty': json_value.get('XML', {}).get('code', 0),
            'js_lines_qty': json_value.get('JavaScript', {}).get('code', 0),
            'css_lines_qty': json_value.get('CSS', {}).get('code', 0),
        }
