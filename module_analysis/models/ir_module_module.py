# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
from pathlib import Path

from pygount import SourceAnalysis

from odoo import api, fields, models
from odoo.modules.module import get_module_path
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    author_ids = fields.Many2many(
        string="Authors",
        comodel_name="ir.module.author",
        readonly=True,
        relation="ir_module_module_author_rel",
    )

    module_type_id = fields.Many2one(
        string="Module Type", comodel_name="ir.module.type", readonly=True
    )

    python_code_qty = fields.Integer(string="Python Code Quantity", readonly=True)

    xml_code_qty = fields.Integer(string="XML Code Quantity", readonly=True)

    js_code_qty = fields.Integer(string="JS Code Quantity", readonly=True)

    css_code_qty = fields.Integer(string="CSS Code Quantity", readonly=True)

    # Overloadable Section
    @api.model
    def _get_analyse_settings(self):
        """Return a dictionnary of data analysed
        Overload this function if you want to analyse other data
        {
            'extension': {
                'data_to_analyse': 'field_name',
            },
        }, [...]
        extension: extension of the file, with the '.'
        data_to_analyse : possible value : code, documentation, empty, string
        field_name: Odoo field name to store the analysis
        """
        return {
            ".py": {"code": "python_code_qty"},
            ".xml": {"code": "xml_code_qty"},
            ".js": {"code": "js_code_qty"},
            ".css": {"code": "css_code_qty"},
        }

    @api.model
    def _get_clean_analyse_values(self):
        """List of fields to unset when a module is uninstalled"""
        return {
            "author_ids": [(6, 0, [])],
            "module_type_id": False,
            "python_code_qty": False,
            "xml_code_qty": 0,
            "js_code_qty": 0,
            "css_code_qty": 0,
        }

    @api.model
    def _get_module_encoding(self, file_ext):
        return "utf-8"

    # Overload Section
    @api.model
    def update_list(self):
        res = super().update_list()
        if self.env.context.get("analyse_installed_modules", False):
            self.search([("state", "=", "installed")]).button_analyse_code()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("state", False) == "installed":
            self.button_analyse_code()
        elif vals.get("state", False) == "uninstalled" and "module_analysis" not in [
            x.name for x in self
        ]:
            self.write(self._get_clean_analyse_values())
        return res

    # Public Section
    def button_analyse_code(self):
        IrModuleAuthor = self.env["ir.module.author"]
        IrModuleTypeRule = self.env["ir.module.type.rule"]
        rules = IrModuleTypeRule.search([])

        cfg = self.env["ir.config_parameter"]
        val = cfg.get_param("module_analysis.exclude_directories", "")
        exclude_directories = [x.strip() for x in val.split(",") if x.strip()]
        val = cfg.get_param("module_analysis.exclude_files", "")
        exclude_files = [x.strip() for x in val.split(",") if x.strip()]

        for module in self:
            _logger.info("Analysing Code for module %s ..." % (module.name))

            # Update Authors, based on manifest key
            authors = []
            if module.author and module.author[0] == "[":
                author_txt_list = safe_eval(module.author)
            else:
                author_txt_list = (module.author and module.author.split(",")) or []

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
            module_path = get_module_path(module.name)

            # Get Files
            analysed_datas = self._get_analyse_data_dict()
            file_extensions = analysed_datas.keys()
            file_list = self._get_files_to_analyse(
                module_path, file_extensions, exclude_directories, exclude_files
            )

            for file_path, file_ext in file_list:
                file_res = SourceAnalysis.from_file(
                    file_path, "", encoding=self._get_module_encoding(file_ext)
                )
                for k, v in analysed_datas.get(file_ext).items():
                    v["value"] += getattr(file_res, k)

            # Update the module with the datas
            values = {}
            for analyses in analysed_datas.values():
                for v in analyses.values():
                    values[v["field"]] = v["value"]
            module.write(values)

    # Custom Section
    @api.model
    def _get_files_to_analyse(
        self, path, file_extensions, exclude_directories, exclude_files
    ):
        res = []
        if not path:
            return res
        for root, _, files in os.walk(path, followlinks=True):
            if set(Path(root).parts) & set(exclude_directories):
                continue
            for name in files:
                if name in exclude_files:
                    continue
                filename, file_extension = os.path.splitext(name)
                if file_extension in file_extensions:
                    res.append((os.path.join(root, name), file_extension))
        return res

    @api.model
    def _get_analyse_data_dict(self):
        res_dict = self._get_analyse_settings().copy()
        for analyse_dict in res_dict.values():
            for analyse_type, v in analyse_dict.items():
                analyse_dict[analyse_type] = {"field": v, "value": 0}
        return res_dict
