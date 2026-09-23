# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GenerateCompanySequencesWizard(models.TransientModel):
    _name = "generate.company.sequences.wizard"
    _description = "Generate Sequences for Company"

    company_ids = fields.Many2many(
        "res.company",
        required=True,
        string="Companies",
        domain="[('id', 'in', allowed_company_ids)]",
    )
    template_ids = fields.Many2many(
        "ir.sequence.template", required=True, string="Sequence Templates"
    )

    @api.model
    def _extract_placeholders(self, template_str):
        if not template_str:
            return set()
        all_placeholders = re.findall(r"%\(([\w\.]+)\)s", template_str)
        return {p for p in all_placeholders if p.startswith("company_id.")}

    @api.model
    def replace_company_placeholders(self, template, company_values):
        if not template:
            return ""

        def repl(match):
            key = match.group(1)
            if key.startswith("company_id."):
                return str(company_values.get(key, match.group(0)))
            return match.group(0)

        return re.sub(r"%\(([\w\.]+)\)s", repl, template)

    @api.model
    def _read_company_data(self, fields_to_read):
        field_names = {p.split(".", 1)[1] for p in fields_to_read}
        company_data = {}
        try:
            for company in self.company_ids:
                data = company.read(list(field_names))[0]
                company_data[company.id] = {
                    f"company_id.{k}": v for k, v in data.items()
                }
        except ValueError as e:
            raise ValidationError(
                f"One or more fields used in the templates does not exist for "
                f"the model. Check that all placeholders match actual company "
                f"fields.\nDetails: {str(e)}."
            ) from e
        return company_data

    @api.model
    def _prepare_sequence_vals(self, tmpl, company, prefix, suffix):
        return {
            "name": f"{company.name} {tmpl.name}",
            "code": tmpl.code,
            "prefix": prefix,
            "suffix": suffix,
            "padding": tmpl.padding,
            "company_id": company.id,
            "number_increment": tmpl.number_increment,
            "implementation": tmpl.implementation,
            "template_id": tmpl.id,
        }

    def action_generate(self):
        fields_to_read = set()
        for tmpl in self.template_ids:
            fields_to_read |= self._extract_placeholders(tmpl.prefix)
            fields_to_read |= self._extract_placeholders(tmpl.suffix)
        company_data = self._read_company_data(fields_to_read)
        for company in self.company_ids:
            values = company_data[company.id]
            missing = [f for f in fields_to_read if not values.get(f)]
            if missing:
                raise ValidationError(
                    self.env._(
                        f"Company '{company.name}' has empty or invalid values "
                        f"for the following fields used in templates: "
                        f"{', '.join(missing)}. Please fill them before "
                        f"generating sequences."
                    )
                )
            for tmpl in self.template_ids:
                prefix = self.replace_company_placeholders(tmpl.prefix, values)
                suffix = self.replace_company_placeholders(tmpl.suffix, values)
                seq_vals = self._prepare_sequence_vals(tmpl, company, prefix, suffix)
                self.env["ir.sequence"].create(seq_vals)
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
