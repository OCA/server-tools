# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models

from .models_mixin import TestMixin

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug("Cannot `import slugify`.")


class UrlBackendFake(models.Model, TestMixin):

    _name = "url.backend.fake"
    _description = "Url Backend"

    name = fields.Char(required=True)


class ResPartnerAddressableFake(models.Model, TestMixin):
    _name = "res.partner.addressable.fake"
    _inherit = "abstract.url"
    _inherits = {"res.partner": "record_id"}
    _description = "Fake partner addressable"

    backend_id = fields.Many2one(comodel_name="url.backend.fake")

    @api.depends("lang_id", "record_id.name")
    def _compute_automatic_url_key(self):
        key_by_id = {}
        for record in self.with_context(lang=self.lang_id.code):
            key_by_id[record.id] = slugify(record.name)
        for record in self:
            record.automatic_url_key = key_by_id[record.id]
