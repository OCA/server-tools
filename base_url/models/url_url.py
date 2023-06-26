#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class UrlUrl(models.Model):
    _name = "url.url"
    _description = "Url"
    _order = "res_model,res_id,redirect desc"

    manual = fields.Boolean(default=True, readonly=True)
    key = fields.Char(required=True, index=True)
    res_id = fields.Many2oneReference(
        string="Record ID",
        help="ID of the target record in the database",
        model_field="res_model",
        readonly=True,
        index=True,
    )
    res_model = fields.Selection(
        selection=lambda s: s._get_model_with_url_selection(), readonly=True, index=True
    )
    redirect = fields.Boolean(help="If tick this url is a redirection to the new url")
    referential = fields.Selection(
        selection=lambda s: s._get_all_referential(),
        index=True,
        default="global",
        required=True,
    )
    lang_id = fields.Many2one("res.lang", "Lang", index=True, required=True)
    need_refresh = fields.Boolean()

    _sql_constraints = [
        (
            "unique_key_per_referential_per_lang",
            "unique(key, referential, lang_id)",
            "Already exists in database",
        )
    ]

    def init(self):
        self.env.cr.execute(
            f"""CREATE UNIQUE INDEX IF NOT EXISTS main_url_uniq
            ON {self._table} (referential, lang_id, res_id, res_model)
            WHERE redirect = False"""
        )
        return super().init()

    @tools.ormcache()
    @api.model
    def _get_model_with_url_selection(self):
        return [
            (model, self.env[model]._description)
            for model in self.env
            if (
                hasattr(self.env[model], "_have_url")
                and not self.env[model]._abstract
                and not self.env[model]._transient
            )
        ]

    def _get_all_referential(self):
        """Return the list of referential for your url, by default it's global
        but you can do your own implementation to have url per search engine
        index for example
        """
        return [("global", "Global")]
