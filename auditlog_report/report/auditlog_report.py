# Copyright 2021 Ecosoft Co., Ltd. <http://ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, tools


class AuditlogReport(models.Model):
    _name = "auditlog.report"
    _description = "Audit Log Report"
    _auto = False
    _order = "id desc"

    # Logs
    create_date = fields.Datetime()
    name = fields.Char(string="Resource Name")
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        readonly=True,
    )
    model_name = fields.Char(readonly=True)
    model_model = fields.Char(string="Technical Model Name", readonly=True)
    res_id = fields.Integer(string="Resource ID", readonly=True)
    user_id = fields.Many2one(comodel_name="res.users", string="User", readonly=True)
    method = fields.Char(readonly=True)
    http_session_id = fields.Many2one("auditlog.http.session", string="Session")
    http_request_id = fields.Many2one("auditlog.http.request", string="HTTP Request")
    # Lines
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field",
        readonly=True,
    )
    old_value = fields.Text(
        readonly=True,
    )
    new_value = fields.Text(
        readonly=True,
    )
    old_value_text = fields.Text(string="Change From", readonly=True)
    new_value_text = fields.Text(string="Change To", readonly=True)
    field_name = fields.Char(string="Technical Field Name", readonly=True)
    field_description = fields.Char(string="Field Name", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as (%s FROM %s)""" %
            (self._table, self._select(), self._from())
        )

    def _select(self):
        select_str = """
            SELECT l.id, l.create_date, a.name, a.model_id, a.model_name,
                a.model_model, a.res_id, a.user_id, a.method,
                a.http_session_id, a.http_request_id,
                l.field_id, l.old_value, l.new_value, l.old_value_text,
                l.new_value_text, l.field_name, l.field_description
        """
        return select_str

    def _from(self):
        from_str = """
            auditlog_log a
            join auditlog_log_line l on (l.log_id=a.id)
        """
        return from_str

