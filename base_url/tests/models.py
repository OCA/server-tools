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


class ResPartner(models.Model, TestMixin):
    _name = "res.partner"
    _inherit = "res.partner"
    _test_teardown_no_delete = True
    _test_purge_fields = ["binding_ids"]

    binding_ids = fields.One2many("res.partner.addressable.fake", "record_id")


class ResPartnerAddressableFake(models.Model, TestMixin):
    _name = "res.partner.addressable.fake"
    _inherit = "abstract.url"
    _inherits = {"res.partner": "record_id"}
    _description = "Fake partner addressable"

    backend_id = fields.Many2one(comodel_name="url.backend.fake")
    special_code = fields.Char()

    @api.depends("lang_id", "special_code", "record_id.name")
    def _compute_automatic_url_key(self):
        self._generic_compute_automatic_url_key()

    def _get_url_keywords(self):
        res = super(ResPartnerAddressableFake, self)._get_url_keywords()
        if self.special_code:
            res += [self.special_code]
        return res
