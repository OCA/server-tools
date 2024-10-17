# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

DEFAULT_PYTHON_CODE = """# Available variables:
#  - records: recordset of all records which need to be filtered
#  - model: Model of records in recordset; is a void recordset
# To return the filtered recordset assing to: res = {...}\n\n\n\n"""


class BaseOnchangeRule(models.Model):
    _name = "base.onchange.rule"
    _description = "Base Onchange Rule"
    _order = "sequence"

    active = fields.Boolean(default=False, tracking=True)
    name = fields.Char(string="Rule Name", required=True)
    description = fields.Text()
    model = fields.Many2one(
        "ir.model", domain=lambda self: [("model", "!=", self._name)], required=True
    )
    model_name = fields.Char(related="model.model")
    code = fields.Text(
        "Python Code",
        default=DEFAULT_PYTHON_CODE,
    )
    sequence = fields.Integer(string="Sequence", required=True, default=10)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    fields_lines = fields.One2many(
        "ir.server.object.lines",
        "base_onchange_rule_id",
        string="Value Mapping",
        copy=True,
    )
    onchange_fields = fields.Many2many(
        "ir.model.fields", domain="[('model_id', '=', model_name)]"
    )

    def evaluate_rules(self, records):
        model_has_company = "company_id" in records._fields
        env_company = self.env["res.company"].browse(
            self.env.context.get("company_id") or self.env.company.id
        )
        companies = env_company
        if model_has_company:
            companies |= records.mapped("company_id")
        for company in companies:
            # 1. Filter records matching the same company
            if model_has_company:
                company_matching = records.filtered(
                    lambda r: (r.company_id or env_company) == company
                )
                company_matching = company_matching.with_context(company_id=company.id)
            else:
                company_matching = records
            # 2. Filter rules matching the same company
            rules = self.filtered(lambda r: r.company_id == company or not r.company_id)
            for rule in rules:
                # 3. Filter records matching the onchange conditions
                records_matching = rule._evaluate_py_code(company_matching)
                if not records_matching:
                    continue
                # 4. Get values to be written
                res = {}
                for exp in rule.fields_lines:
                    res[exp.col1.name] = exp.eval_value()[exp.id]
                # 5. Update values
                records_matching.update(res)

    def _evaluate_py_code(self, records):
        self.ensure_one()
        expr = self.code
        space = {"records": records, "model": self.env[records._name]}
        try:
            safe_eval(expr, space, mode="exec", nocopy=True)
        except Exception as e:
            raise UserError(_("Error when the code in:\n %s \n\n(%s)") % (self.name, e))
        return space.get("res", False)


class IrServerObjectLines(models.Model):
    _inherit = "ir.server.object.lines"

    base_onchange_rule_id = fields.Many2one(
        "base.onchange.rule",
        string="Related Base Onchange Rule",
        ondelete="cascade",
    )
    onchange_rule_model_name = fields.Char()
