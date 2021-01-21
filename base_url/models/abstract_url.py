#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug("Cannot `import slugify`.")


def get_model_ref(record):
    return "{},{}".format(record._name, record.id)


class AbstractUrl(models.AbstractModel):
    _name = "abstract.url"
    _description = "Abstract Url"

    url_builder = fields.Selection(
        selection=[("auto", "Automatic"), ("manual", "Manual")], default="auto"
    )
    automatic_url_key = fields.Char(compute="_compute_automatic_url_key", store=True)
    manual_url_key = fields.Char()
    url_key = fields.Char(string="Url key", compute="_compute_url_key", store=True)
    url_url_ids = fields.One2many(
        compute="_compute_url_url_ids", comodel_name="url.url"
    )
    redirect_url_url_ids = fields.One2many(
        compute="_compute_redirect_url_url_ids", comodel_name="url.url"
    )
    lang_id = fields.Many2one("res.lang", string="Lang", required=True)
    is_urls_sync_required = fields.Boolean(
        compute="_compute_is_urls_sync_required", store=True
    )
    active = fields.Boolean(string="Active", default=True)

    @api.constrains("url_builder", "manual_url_key")
    def _check_manual_url_key(self):
        for rec in self:
            if rec.url_builder == "manual" and not rec.manual_url_key:
                raise ValidationError(
                    _("Manual url key is required if builder is set to manual")
                )

    @api.onchange("manual_url_key")
    def on_url_key_change(self):
        self.ensure_one()
        if self.manual_url_key:
            url = slugify(self.manual_url_key)
            if url != self.manual_url_key:
                self.manual_url_key = url
                return {
                    "warning": {
                        "title": "Adapt text rules",
                        "message": "it will be adapted to %s" % url,
                    }
                }

    @api.depends("url_key")
    def _compute_is_urls_sync_required(self):
        for record in self:
            record.is_urls_sync_required = True

    def _get_url_keywords(self):
        """This method return a list of keyword that will be concatenated
        with '-' to generate the url
        Ex: if you return ['foo', '42'] the url will be foo-42

        Note the self already include in the context the lang of the record
        """
        self.ensure_one()
        # TODO: IMO we should add the ID here by default
        # to make sure the URL is always unique
        return [self.name]

    def _post_process_url_key(self, key):
        """This method allow you to customized the url key.
        you can use it to build full path be adding the url of parent record
        Ex: key is 42 you can prefix it with "foo" and so return "foo/42"

        Note: the self do not include in the context the lang of the record
        """
        self.ensure_one()
        return key

    def _generic_compute_automatic_url_key(self):
        records_by_lang = defaultdict(self.browse)
        for record in self:
            records_by_lang[record.lang_id] |= record

        key_by_id = {}
        for lang_id, records in records_by_lang.items():
            for record in records.with_context(lang=lang_id.code):
                if not isinstance(record.id, models.NewId):
                    key_by_id[record.id] = slugify("-".join(record._get_url_keywords()))

        for record in self:
            if not isinstance(record.id, models.NewId):
                record.automatic_url_key = record._post_process_url_key(
                    key_by_id[record.id]
                )
            else:
                record.automatic_url_key = False

    def _compute_automatic_url_key_depends(self):
        return ["lang_id", "record_id.name"]

    @api.depends(lambda self: self._compute_automatic_url_key_depends())
    def _compute_automatic_url_key(self):
        raise NotImplementedError(
            "Automatic url key must be computed in concrete model"
        )

    @api.depends("manual_url_key", "automatic_url_key", "url_builder", "active")
    def _compute_url_key(self):
        for record in self:
            if not record.active:
                record.url_key = ""
            else:
                if record.url_builder == "manual":
                    new_url = record.manual_url_key
                else:
                    new_url = record.automatic_url_key
                record.url_key = new_url

    def _compute_redirect_url_url_ids(self):
        for record in self:
            record.redirect_url_url_ids = record.env["url.url"].search(
                [
                    ("model_id", "=", get_model_ref(record)),
                    ("redirect", "=", True),
                ]
            )

    def _compute_url_url_ids(self):
        for record in self:
            record.url_url_ids = record.env["url.url"].search(
                [("model_id", "=", get_model_ref(record))]
            )

    @api.model
    def _prepare_url(self, url_key):
        return {
            "url_key": url_key,
            "redirect": False,
            "model_id": get_model_ref(self),
        }

    def _reuse_url(self, existing_url):
        # TODO add user notification in the futur SEO dashboard
        existing_url.write({"model_id": get_model_ref(self), "redirect": False})

    def set_url(self, url_key):
        """Se a new url
        backup old url

        1 find url redirect true and same model_id
        if other model id refuse
        2 if exists set to False

        3 write the new one
        """
        self.ensure_one()
        existing_url = self.env["url.url"].search(
            [
                ("url_key", "=", url_key),
                ("backend_id", "=", get_model_ref(self.backend_id)),
                ("lang_id", "=", self.lang_id.id),
            ]
        )
        if existing_url:
            if self != existing_url.model_id:
                if existing_url.redirect:
                    self._reuse_url(existing_url)
                else:
                    raise UserError(
                        _(
                            "Url_key already exist in other model"
                            "\n- name: %s\n - id: %s\n"
                            "- url_key: %s\n - url_key_id %s"
                        )
                        % (
                            existing_url.model_id.name,
                            existing_url.model_id.id,
                            existing_url.url_key,
                            existing_url.id,
                        )
                    )
            else:
                existing_url.write({"redirect": False})
        else:
            # no existing key creating one if not empty
            self.env["url.url"].create(self._prepare_url(url_key))
        # other url of object set redirect to True
        redirect_urls = self.env["url.url"].search(
            [
                ("model_id", "=", get_model_ref(self)),
                ("url_key", "!=", url_key),
                ("redirect", "=", False),
            ]
        )
        redirect_urls.write({"redirect": True})
        # we must explicitly invalidate the cache since there is no depends
        # defined on this computed fields and this field could have already
        # been loaded into the cache
        self.invalidate_cache(fnames=["url_url_ids"], ids=self.ids)

    def _redirect_existing_url(self):
        """
        This method is called when the record is deactivated to give a chance
        to the concrete model to implement a redirect strategy
        """
        return True

    def _sync_urls(self):
        """
        This method is in charge of syncing the url.url object related to
        the current model
        """
        records = self.filtered("is_urls_sync_required")
        for record in records:
            if not record.active:
                record._redirect_existing_url()
            else:
                record.set_url(record.url_key)
        return records

    @api.model
    def create(self, value):
        res = super(AbstractUrl, self).create(value)
        # without this flush we have cases where the url_key is not stored
        self.flush()
        synced = res._sync_urls()
        super(AbstractUrl, synced).write({"is_urls_sync_required": False})
        return res

    def write(self, value):
        res = super(AbstractUrl, self).write(value)
        # without this flush we have cases where the url_key is not stored
        self.flush()
        synced = self._sync_urls()
        super(AbstractUrl, synced).write({"is_urls_sync_required": False})
        return res

    def unlink(self):
        for record in self:
            # TODO we should propose to redirect the old url
            urls = record.env["url.url"].search(
                [("model_id", "=", get_model_ref(record))]
            )
            urls.unlink()
        self.flush()
        return super(AbstractUrl, self).unlink()
