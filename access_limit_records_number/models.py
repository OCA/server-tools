from odoo import api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _


class BaseLimitRecordsNumber(models.Model):
    _name = "base.limit.records_number"
    _description = "Restrictions for number of records"
    _inherits = {"base.automation": "base_automation_id"}

    base_automation_id = fields.Many2one(
        "base.automation", "Base Automation", required=True, ondelete="cascade"
    )
    max_records = fields.Integer(string="Maximum Records", required=True)
    domain = fields.Char(string="Domain", default="[]")

    @api.constrains('max_records')
    def _check_max_records_is_positive_or_false(self):
        for record in self:
            if record.max_records <= 0:
                raise exceptions.ValidationError("'max_records' can not be negative or zero")

    @api.model
    def _clean_domain(self, vals):
        if "domain" in vals and vals["domain"].replace(" ", "") == "[]":
            vals["domain"] = False

    def create(self, vals_list):
        for vals in vals_list:
            self._clean_domain(vals)

        automations = super(BaseLimitRecordsNumber, self).create(vals_list)

        for automation in automations:
            action = {
                'name': 'Restrict number of records',
                'usage': 'base_automation',
                'model_id': automation.model_id,
                "base_automation_id": automation.id,
                "state": "code",
                "code": "env['base.limit.records_number'].verify_table()"
            }
            automation.write({"action_server_ids": [fields.Command.create(action)]})

        return automations

    def write(self, vals):
        self._clean_domain(vals)

        return super(BaseLimitRecordsNumber, self).write(vals)

    @api.model
    def default_get(self, default_fields):
        res = super(BaseLimitRecordsNumber, self).default_get(default_fields)
        res["trigger"] = "on_create_or_write"
        return res

    @api.model
    def verify_table(self):
        """ Get parameters and verify. Raise exception if limit """
        model_name = self.env.context["active_model"]
        for automation in self.search([("model_id.model", "=", model_name), ()]):
            if automation.domain:
                domain = safe_eval(automation.domain)
            else:
                domain = []

            records_count = self.env[model_name].search_count(domain)
            if records_count > automation.max_records:
                raise exceptions.UserError(
                    _(
                        'Maximimum allowed records in table "%(model_name)s" is %(max_records)s, while after this update you would have %(records_count)s'
                    )
                    % {
                        "model_name": automation.model_id.name,
                        "max_records": automation.max_records,
                        "records_count": records_count,
                    }
                )