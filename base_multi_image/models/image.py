# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import io
import logging
import os
import re

import requests
from PIL import Image as PILImage

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import config

from odoo.addons.base_import.models.base_import import (
    DEFAULT_IMAGE_CHUNK_SIZE,
    DEFAULT_IMAGE_MAXBYTES,
    DEFAULT_IMAGE_REGEX,
    DEFAULT_IMAGE_TIMEOUT,
)

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
    owner_id = fields.Integer(string="Owner", required=True)
    owner_model = fields.Char(required=True)
    owner_ref_id = fields.Reference(
        selection="_selection_owner_ref_id",
        string="Referenced Owner",
        compute="_compute_owner_ref_id",
        store=True,
    )
    name = fields.Char(string="Image title", translate=True)
    load_from = fields.Char(
        string="Load from",
        help="Either a remote url or a file path on the server",
        store=False,
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
                s.owner_ref_id = f"{s.owner_model},{s.owner_id}"

    @api.depends("owner_id", "owner_model")
    def _compute_show_technical(self):
        """Know if you need to show the technical fields."""
        self.show_technical = all(
            "default_owner_%s" % f not in self.env.context for f in ("id", "model")
        )

    @api.onchange("load_from")
    def _onchange_load_from(self):
        if not self.load_from:
            return
        if re.match(
            config.get("import_image_regex", DEFAULT_IMAGE_REGEX), self.load_from
        ):
            # Retrieve from remote url
            self.image_1920 = self._get_image_from_url(self.load_from)
            filename = self.load_from.split("/")[-1]
            self.name, self.extension = os.path.splitext(filename)
        else:
            self.image_1920 = self._get_image_from_file(self.load_from)
            self.name, self.extension = os.path.splitext(
                os.path.basename(self.load_from)
            )
        self.name = self._make_name_pretty(self.name)
        self.load_from = False

    @api.model
    def _get_image_from_file(self, path):
        allowed_paths = tools.config.get("readable_folders", "")
        if not allowed_paths:
            raise UserError(_("The image %s doesn't exist", path))
        allowed_paths = allowed_paths and allowed_paths.split(",") or []
        file_path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

        if (
            file_path
            and os.path.exists(file_path)
            and any(file_path.startswith(p) for p in allowed_paths)
        ):
            try:
                with open(file_path, "rb") as f:
                    return base64.b64encode(f.read())
            except Exception as e:
                raise UserError(
                    _(
                        "Can not open the image %(path)s, error : %(error)s",
                        path=path,
                        error=e,
                        exc_info=True,
                    )
                ) from e
        else:
            raise UserError(_("The image %s doesn't exist", path))

        return False

    @api.model
    def _get_image_from_url(self, url):
        with requests.Session() as session:
            session.stream = True
            # Same code as base_import._import_image_by_url
            maxsize = int(config.get("import_image_maxbytes", DEFAULT_IMAGE_MAXBYTES))
            try:
                response = session.get(
                    url,
                    timeout=int(
                        config.get("import_image_timeout", DEFAULT_IMAGE_TIMEOUT)
                    ),
                )
                response.raise_for_status()

                if (
                    response.headers.get("Content-Length")
                    and int(response.headers["Content-Length"]) > maxsize
                ):
                    raise UserError(
                        _("File size exceeds configured maximum (%s bytes)", maxsize)
                    )

                content = bytearray()
                for chunk in response.iter_content(DEFAULT_IMAGE_CHUNK_SIZE):
                    content += chunk
                    if len(content) > maxsize:
                        raise UserError(
                            _(
                                "File size exceeds configured maximum (%s bytes)",
                                maxsize,
                            )
                        )

                image = PILImage.open(io.BytesIO(content))
                w, h = image.size
                if w * h > 42e6:  # Nokia Lumia 1020 photo resolution
                    raise UserError(
                        _(
                            "Image size excessive, "
                            "imported images must be smaller than 42 million pixel"
                        )
                    )

                return base64.b64encode(content)
            except Exception as e:
                _logger.exception(e)
                raise UserError(
                    _("Could not retrieve URL: %(url)s: %(error)s", url=url, error=e)
                ) from e

    @api.model
    def _make_name_pretty(self, name):
        return name.replace("_", " ").capitalize()

    @api.onchange("filename")
    def _onchange_filename(self):
        if self.filename:
            self.name, self.extension = os.path.splitext(self.filename)
            self.name = self._make_name_pretty(self.name)
