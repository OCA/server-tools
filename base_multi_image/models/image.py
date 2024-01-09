# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
import os
from urllib.error import ContentTooShortError
from urllib.request import urlretrieve

from odoo import _, api, exceptions, fields, models, tools

_logger = logging.getLogger(__name__)


class Image(models.Model):
    _name = "base_multi_image.image"
    _inherit = "image.mixin"
    _order = "sequence, owner_model, owner_id, id"
    _description = """ image model for multiple image functionality """
    _sql_constraints = [
        (
            "uniq_name_owner",
            "UNIQUE(owner_id, owner_model, name)",
            _("A document can have only one image with the same name."),
        ),
    ]

    # This Integer is really a split Many2one
    owner_id = fields.Integer("Owner", required=True)
    owner_model = fields.Char(required=True)
    owner_ref_id = fields.Reference(
        selection="_selection_owner_ref_id",
        string="Referenced Owner",
        compute="_compute_owner_ref_id",
        store=True,
    )
    storage = fields.Selection(
        [
            ("url", "URL"),
            ("file", "OS file"),
            ("db", "Database"),
            ("filestore", "Filestore"),
        ],
        required=True,
        default="filestore",
    )
    name = fields.Char("Image title", translate=True)
    filename = fields.Char()
    extension = fields.Char("File extension", readonly=True)
    attachment_id = fields.Many2one(
        "ir.attachment", string="Attachment", domain="[('index_content', '=', 'image')]"
    )
    file_db_store = fields.Binary("Image( stored in database)", attachment=False)
    path = fields.Char("Image path", help="Image path")
    url = fields.Char("Image remote URL")
    attachment_image = fields.Image("Image")
    image_1920 = fields.Image(
        "Full-sized image",
        max_width=1920,
        max_height=1920,
        # store=True,
        compute="_compute_image",
    )
    comments = fields.Text(translate=True)
    sequence = fields.Integer(default=10)
    show_technical = fields.Boolean(compute="_compute_show_technical")

    @api.model
    @tools.ormcache("self")
    def _selection_owner_ref_id(self):
        """Allow any model; after all, this field is readonly."""
        return [(r.model, r.name) for r in self.env["ir.model"].search([])]

    @api.depends("owner_model", "owner_id")
    def _compute_owner_ref_id(self):
        """Get a reference field based on the split model and id fields."""
        for s in self:
            if s.owner_model:
                s.owner_ref_id = "{0.owner_model},{0.owner_id}".format(s)

    @api.depends("storage", "path", "file_db_store", "url")
    def _compute_image(self):
        """Get image data from the right storage type."""
        for s in self:
            s.image_1920 = getattr(s, "_get_image_from_%s" % s.storage)()

    @api.depends("owner_id", "owner_model")
    def _compute_show_technical(self):
        """Know if you need to show the technical fields."""
        self.show_technical = all(
            "default_owner_%s" % f not in self.env.context for f in ("id", "model")
        )

    def _get_image_from_filestore(self):
        # if self.attachment_id:
        # TODO what if we need to choose images from attachments from the record?
        #    return self.attachment_id.datas
        # else:
        return self.attachment_image

    def _get_image_from_db(self):
        return self.file_db_store

    def _get_image_from_file(self):
        if self.path and os.path.exists(self.path):
            try:
                with open(self.path, "rb") as f:
                    return base64.b64encode(f.read())
            except Exception as e:
                _logger.error(
                    "Can not open the image %s, error : %s", self.path, e, exc_info=True
                )
        else:
            _logger.error("The image %s doesn't exist ", self.path)

        return False

    def _get_image_from_url(self):
        return self._get_image_from_url_cached(self.url)

    @api.model
    @tools.ormcache("url")
    def _get_image_from_url_cached(self, url):
        """Allow to download an image and cache it by its URL."""
        if url:
            try:
                (filename, header) = urlretrieve(url)
                with open(filename, "rb") as f:
                    return base64.b64encode(f.read())
            except ContentTooShortError:
                _logger.error("URL %s cannot be fetched", url, exc_info=True)

        return False

    @api.model
    def _make_name_pretty(self, name):
        return name.replace("_", " ").capitalize()

    @api.onchange("url")
    def _onchange_url(self):
        if self.url:
            filename = self.url.split("/")[-1]
            self.name, self.extension = os.path.splitext(filename)
            self.name = self._make_name_pretty(self.name)

    @api.onchange("path")
    def _onchange_path(self):
        if self.path:
            self.name, self.extension = os.path.splitext(os.path.basename(self.path))
            self.name = self._make_name_pretty(self.name)

    @api.onchange("filename")
    def _onchange_filename(self):
        if self.filename:
            self.name, self.extension = os.path.splitext(self.filename)
            self.name = self._make_name_pretty(self.name)

    @api.onchange("attachment_id")
    def _onchange_attachmend_id(self):
        if self.attachment_id:
            self.name = self.attachment_id.res_name

    @api.constrains("storage", "url")
    def _check_url(self):
        for record in self:
            if record.storage == "url" and not record.url:
                raise exceptions.ValidationError(
                    _("You must provide an URL for the image.")
                )

    @api.constrains("storage", "path")
    def _check_path(self):
        for record in self:
            if record.storage == "file" and not record.path:
                raise exceptions.ValidationError(
                    _("You must provide a file path for the image.")
                )

    @api.constrains("storage", "file_db_store")
    def _check_store(self):
        for record in self:
            if record.storage == "db" and not record.file_db_store:
                raise exceptions.ValidationError(
                    _("You must upload image to store in database.")
                )

    @api.constrains("storage", "attachment_id")
    def _check_attachment_id(self):
        for record in self:
            if record.storage == "filestore" and not record.attachment_image:
                raise exceptions.ValidationError(_("You must upload image."))
