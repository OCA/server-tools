#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

from .abstract_url import get_model_ref

_logger = logging.getLogger(__name__)


class UrlUrl(models.Model):

    _name = "url.url"
    _description = "Url"

    url_key = fields.Char(required=True)
    model_id = fields.Reference(
        selection="_selection_target_model",
        help="The id of content linked to the url.",
        readonly=True,
        string="Model",
        required=True,
    )
    redirect = fields.Boolean(
        help="If tick this url is a redirection to the new url"
    )
    backend_id = fields.Reference(
        selection="_selection_target_model",
        compute="_compute_related_fields",
        store=True,
        help="Backend linked to this URL",
        string="Backend",
    )
    lang_id = fields.Many2one(
        "res.lang", "Lang", compute="_compute_related_fields", store=True
    )

    _sql_constraints = [
        (
            "unique_key_per_backend_per_lang",
            "unique(url_key, backend_id, lang_id)",
            "Already exists in database",
        )
    ]

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    @api.depends("model_id")
    def _compute_related_fields(self):
        for record in self:
            record.backend_id = get_model_ref(record.model_id.backend_id)
            record.lang_id = record.model_id.lang_id

    @api.model
    def _reference_models(self):
        return []

    def _get_object(self, url):
        """
        :return: return object attach to the url
        """
        return self.search([("url_key", "=", url)]).model_id
