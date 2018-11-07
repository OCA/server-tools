# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


def get_model_ref(record):
    return "%s,%s" % (record._name, record.id)


class UrlUrl(models.Model):

    _name = "url.url"

    url_key = fields.Char(required=True)
    model_id = fields.Reference(
        selection=[],
        help="The id of content linked to the url.",
        readonly=True,
        string="Model",
        required=True)
    redirect = fields.Boolean(
        help="If tick this url is a redirection to the new url")
    backend_id = fields.Reference(
        selection=[],
        compute='_compute_related_fields',
        store=True,
        help="Backend linked to this URL",
        string="Backend")
    lang_id = fields.Many2one(
        'res.lang',
        'Lang',
        compute='_compute_related_fields',
        store=True)

    _sql_constraints = [('unique_key_per_backend_per_lang',
                         'unique(url_key, backend_id, lang_id)',
                         'Already exists in database')]

    @api.depends('model_id')
    def _compute_related_fields(self):
        for record in self:
            record.backend_id = get_model_ref(record.model_id.backend_id)
            record.lang_id = record.model_id.lang_id

    @api.model
    def _reference_models(self):
        return []

    @api.model
    def create(self, vals):
        """
        Inherit the create to remove existing url in some case
        :param vals: dict
        :return: self recordset
        """
        url = vals.get('url_key')
        backend_id = vals.get('backend_id')
        lang_id = vals.get('lang_id')
        self._clean_existing_redirect(url, backend_id, lang_id)
        return super(UrlUrl, self).create(vals)

    @api.model
    def _clean_existing_redirect(self, url, backend_id, lang_id):
        """
        If a new URL is created (related to the same backend) and the existing
        is a redirect, we have to remove them to give priority to the new url.
        :param url: str
        :param backend_id: str (because it's a reference field)
        :param lang_id: int
        :return: bool
        """
        domain = [
            ('url_key', '=', url),
            ('redirect', '=', True),
            ('backend_id', '=', backend_id),
            ('lang_id', '=', lang_id),
        ]
        old_url = self.search(domain)
        if old_url:
            old_url.unlink()
        return True

    def _get_object(self, url):
        """
        :return: return object attach to the url
        """
        return self.search([('url_key', "=", url)]).model_id
