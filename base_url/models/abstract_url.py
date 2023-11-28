#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.base_sparse_field.models.fields import Serialized

DEFAULT_LANG = "en_US"

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug("Cannot `import slugify`.")


SMART_BUTTON = """
<button class="oe_stat_button"
       name="open_url"
       icon="fa-list-ul"
       type="object">
       <div class="o_field_widget o_stat_info">
            <span class="o_stat_value"><field name="count_url"/></span>
            <span>URL</span>
       </div>
</button>"""


class AbstractUrl(models.AbstractModel):
    _name = "abstract.url"
    _description = "Abstract Url"
    _have_url = True

    url_ids = fields.One2many("url.url", "res_id")
    url_need_refresh = fields.Boolean(
        compute="_compute_url_need_refresh", store=True, readonly=False
    )
    count_url = fields.Integer(compute="_compute_count_url")
    url_key = fields.Char(compute="_compute_url_key")
    redirect_url_key = Serialized(
        compute="_compute_url_key", string="Redirect Url Keys"
    )

    def _compute_count_url(self):
        res = self.env["url.url"].read_group(
            domain=[
                ("res_id", "in", self.ids),
                ("res_model", "=", self._name),
            ],
            fields=["res_id"],
            groupby=["res_id"],
        )
        id2count = {item["res_id"]: item["res_id_count"] for item in res}
        for record in self:
            record.count_url = id2count.get(record.id, 0)

    def _compute_url_need_refresh_depends(self):
        return self._get_keyword_fields()

    @api.depends(lambda self: self._compute_url_need_refresh_depends())
    def _compute_url_need_refresh(self):
        for record in self:
            record.url_need_refresh = True

    @api.depends("url_ids")
    @api.depends_context("lang", "referential")
    def _compute_url_key(self):
        referential = self._context.get("referential", "global")
        lang = self._context.get("lang", "en_US")
        for record in self:
            record.url_key = record._get_main_url(referential, lang).key
            record.redirect_url_key = record._get_redirect_urls(
                referential, lang
            ).mapped("key")

    def _get_keyword_fields(self):
        """This method return a list of field that will be concatenated
        with '-' to generate the url
        Ex: if you return ['name', 'code'] the url will be f"{record.name}-{record.code}"

        Note: the self already include in the context the lang of the record
        Note: you can return key like in depends ex: ["categ_id.name", "code"]
        """
        # TODO: IMO we should add the ID here by default
        # to make sure the URL is always unique
        # seb.beau: not sure, most of site do not have id in url
        # the url have an seo impact so it's better to only put meaning information
        # moreover for unicity you can put the default code of the product or ean13
        return ["name"]

    def _generate_url_key(self, referential, lang):
        def get(self, key_path):
            value = self
            for key_field in key_path.split("."):
                value = value[key_field]
            return value

        self.ensure_one()
        return slugify(
            "-".join([get(self, k) for k in self._get_keyword_fields() if get(self, k)])
        )

    def _get_redirect_urls(self, referential, lang):
        self.ensure_one()
        return self.url_ids.filtered(
            lambda s: (
                s.lang_id.code == lang and s.referential == referential and s.redirect
            )
        )

    def _get_main_url(self, referential, lang):
        self.ensure_one()
        return self.url_ids.filtered(
            lambda s: (
                s.lang_id.code == lang
                and s.referential == referential
                and not s.redirect
            )
        )

    @api.model
    def _prepare_url(self, referential, lang, url_key):
        return {
            "key": url_key,
            "redirect": False,
            "res_model": self._name,
            "res_id": self.id,
            "referential": referential,
            "lang_id": self.env["res.lang"]._lang_get_id(lang),
            "manual": False,
        }

    def _reuse_url(self, existing_url):
        # TODO add user notification in the futur SEO dashboard
        existing_url.write(
            {
                "res_model": self._name,
                "res_id": self.id,
                "redirect": False,
            }
        )

    def _update_url_key(self, referential="global", lang=None):
        lang = lang or self.env.context.get("lang", DEFAULT_LANG)
        for record in self.with_context(lang=lang):
            # TODO maybe we should have a computed field that flag the
            # current url if the key used for building the url have changed
            # so we can skip this check if nothing have changed
            current_url = record._get_main_url(referential, lang)
            if not current_url.manual:
                # Updating an url is done for a specific context
                # a lang and a referential
                # if something have changed on the record the url_need_refresh
                # is flagged.
                # Before updating one specific url (referential + lang)
                # the flag is propagated on all valid url
                if record.url_need_refresh:
                    record.url_ids.filtered(
                        lambda s: not s.redirect and not s.manual
                    ).write({"need_refresh": True})
                if not current_url or current_url.need_refresh:
                    current_url.need_refresh = False
                    url_key = record._generate_url_key(referential, lang)
                    # maybe some change have been done but the url is the same
                    # so check it
                    if current_url.key != url_key:
                        current_url.redirect = True
                        record._add_url(referential, lang, url_key)
            if record.url_need_refresh:
                record.url_need_refresh = False

    def _add_url(self, referential, lang, url_key):
        self.ensure_one()
        existing_url = self.env["url.url"].search(
            [
                ("referential", "=", referential),
                ("lang_id.code", "=", lang),
                ("key", "=", url_key),
            ]
        )
        if existing_url:
            if existing_url.redirect:
                self._reuse_url(existing_url)
            else:
                raise UserError(
                    _(
                        "Url_key already exist in other model"
                        "\n- name: %(model_name)s\n - id: %(model_id)s\n"
                        "- url_key: %(url_key)s\n - url_key_id %(url_id)s"
                    )
                    % dict(
                        model_name=existing_url.model_id.name,
                        model_id=existing_url.model_id.id,
                        url_key=existing_url.url_key,
                        url_id=existing_url.id,
                    )
                )

        else:
            vals = self._prepare_url(referential, lang, url_key)
            self.env["url.url"].create(vals)

    def _redirect_existing_url(self, action):
        """
        This method is called when the record is deactivated to give a chance
        to the concrete model to implement a redirect strategy
        action can be "archived" or "unlink"
        """
        return True

    def unlink(self):
        for record in self:
            record._redirect_existing_url("unlink")
            # Remove dead url that have been not redirected
            record.url_ids.unlink()
        return super().unlink()

    def write(self, vals):
        res = super().write(vals)
        if "active" in vals and not vals["active"]:
            self._redirect_existing_url("archived")
        return res

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        button_box = arch.xpath("//div[@name='button_box']")
        if button_box:
            button_box[0].append(etree.fromstring(SMART_BUTTON))
        return arch, view

    def open_url(self):
        self.ensure_one()
        action = self.env.ref("shopinvader_base_url.base_url_action_view").read()[0]
        action["domain"] = [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        action["context"] = {
            "hide_res_model": True,
            "hide_res_id": True,
            "default_res_model": self._name,
            "default_res_id": self.id,
        }
        return action
