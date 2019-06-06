# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class UrlBackendFake(models.Model):
    _name = "url.backend.fake"
    _description = "Url Backend"

    name = fields.Char(required=True)


class ResPartner(models.Model):
    _inherit = "res.partner"

    binding_ids = fields.One2many("res.partner.addressable.fake", "record_id")


class ResPartnerAddressableFake(models.Model):
    _name = "res.partner.addressable.fake"
    _inherit = "abstract.url"
    _inherits = {"res.partner": "record_id"}
    _description = "Fake partner addressable"

    backend_id = fields.Many2one(comodel_name="url.backend.fake")
    special_code = fields.Char()

    @api.depends("lang_id", "special_code", "record_id.name")
    def _compute_automatic_url_key(self):
        self._generic_compute_automatic_url_key()
