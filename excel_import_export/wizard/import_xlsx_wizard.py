# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models
from odoo.exceptions import RedirectWarning, ValidationError


class ImportXLSXWizard(models.TransientModel):
    """This wizard is used with the template (xlsx.template) to import
    xlsx template back to active record"""

    _name = "import.xlsx.wizard"
    _description = "Wizard for importing excel"

    def _domain_template_id(self):
        return (
            "["
            "('res_model', '=', res_model), "
            "('fname', '=', fname), "
            "('gname', '=', False)"
            "] if fname and res_model else []"
        )

    import_file = fields.Binary(string="Import File (*.xlsx)")
    filename = fields.Char("Import File Name")
    template_id = fields.Many2one(
        "xlsx.template",
        string="Template",
        required=True,
        ondelete="cascade",
        domain=lambda self: self._domain_template_id(),
    )
    res_id = fields.Integer(string="Resource ID", readonly=True)
    res_model = fields.Char(string="Resource Model", readonly=True, size=500)
    datas = fields.Binary(string="Sample", related="template_id.datas", readonly=True)
    fname = fields.Char(
        string="Template Name", related="template_id.fname", readonly=True
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Import File(s) (*.xlsx)",
        required=True,
        help="You can select multiple files to import.",
    )
    state = fields.Selection(
        [("choose", "Choose"), ("get", "Get")],
        default="choose",
        help="* Choose: wizard show in user selection mode"
        "\n* Get: wizard show results from user action",
    )

    def check_view_init(self, context):
        """This template only works on some context of active record"""
        res_model = context.get("active_model", False)
        res_id = context.get("active_id", False)
        if not res_model or not res_id:
            return
        record = self.env[res_model].browse(res_id)
        messages = []
        valid = True
        # For all import, only allow import in draft state (for documents)
        import_states = context.get("template_import_states", [])
        if import_states:  # states specified in context, test this
            if "state" in record and record["state"] not in import_states:
                messages.append(
                    self.env._("Document must be in %s states", import_states)
                )
                valid = False
        else:  # no specific state specified, test with draft
            if "state" in record and "draft" not in record["state"]:  # not in
                messages.append(self.env._("Document must be in draft state"))
                valid = False
        # Context testing
        if context.get("template_context", False):
            template_context = context["template_context"]
            for key, value in template_context.items():
                if (
                    key not in record
                    or (
                        record._fields[key].type == "many2one"
                        and record[key].id
                        or record[key]
                    )
                    != value
                ):
                    valid = False
                    messages.append(
                        self.env._(
                            "This import action is not usable "
                            "in this document context"
                        )
                    )
                    break
        if not valid:
            raise ValidationError("\n".join(messages))
        return

    @api.model
    def default_get(self, fields_list):
        context = self.env.context
        res_model = context.get("active_model", False)
        res_id = context.get("active_id", False)
        template_domain = context.get("template_domain", [])
        templates = self.env["xlsx.template"].search(template_domain)
        if not templates:
            raise ValidationError(self.env._("No template found"))
        res = super().default_get(fields_list)
        for template in templates:
            if not template.datas:
                act = self.env.ref("excel_import_export.action_xlsx_template")
                raise RedirectWarning(
                    self.env._(
                        'File "%(fname)s" not found in template, %(name)s.',
                        fname=template.fname,
                        name=template.name,
                    ),
                    act.id,
                    self.env._("Set Templates"),
                )
        self.check_view_init(context)
        res["template_id"] = len(templates) == 1 and template.id or False
        res["res_id"] = res_id
        res["res_model"] = res_model
        return res

    def get_import_sample(self):
        self.ensure_one()
        return {
            "name": self.env._("Import Excel"),
            "type": "ir.actions.act_window",
            "res_model": "import.xlsx.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
            "context": self.env.context.copy(),
        }

    def action_import(self):
        self.ensure_one()
        Import = self.env["xlsx.import"]
        res_ids = []
        if self.import_file:
            record = Import.import_xlsx(
                self.import_file, self.template_id, self.res_model, self.res_id
            )
            res_ids = [record.id]
        elif self.attachment_ids:
            for attach in self.attachment_ids:
                record = Import.import_xlsx(attach.datas, self.template_id)
                res_ids.append(record.id)
        else:
            raise ValidationError(self.env._("Please select Excel file to import"))
        # If redirect_action is specified, do redirection
        if self.template_id.redirect_action:
            vals = self.template_id.redirect_action.read()[0]
            vals["domain"] = [("id", "in", res_ids)]
            return vals
        self.write({"state": "get"})
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }
