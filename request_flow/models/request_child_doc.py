# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RequestChildDoc(models.Model):
    _name = "request.child.doc"
    _description = "Request's Documents"
    _auto = False
    _order = "res_model"
    _rec_name = "id"

    request_id = fields.Many2one(
        comodel_name="request.request",
    )
    res_model = fields.Char(string="Child Doc Model")
    res_id = fields.Integer(string="Record ID")
    doc_ref = fields.Reference(
        string="Document",
        selection=lambda self: self._get_ref_selection(),
    )
    doc_note = fields.Text(
        string="Description",
        compute="_compute_doc_info",
        compute_sudo=True,
    )
    doc_amount = fields.Float(
        string="Amount",
        compute="_compute_doc_info",
        compute_sudo=True,
    )
    doc_status = fields.Char(
        compute="_compute_doc_info",
        string="Status",
        compute_sudo=True,
    )

    @api.model
    def _get_ref_selection(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    def _compute_doc_info(self):
        """ Comput doc info based on child document (extended addons) """
        for rec in self:
            rec._update_doc_info()

    def _update_doc_info(self):
        """ Update doc_note, doc_amount, doc_status """

    def _get_sql(self):
        """ For this base module, make a dummy sql call """
        return [
            """
            select 0 as id,
                0 as request_id,
                0 as res_id,
                ''::char as res_model,
                ''::char as doc_ref
        """
        ]

    @property
    def _table_query(self):
        queries = self._get_sql()
        return " union ".join(queries)
