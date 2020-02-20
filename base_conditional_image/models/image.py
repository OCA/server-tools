# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class Image(models.Model):
    _name = 'image'
    _description = 'Image'

    name = fields.Char('Name', required=True)
    model_name = fields.Char('Model Name', required=True)
    selector = fields.Text(
        'Selector',
        help='Python expression used as selector when multiple images are used'
             'for the same object. The variable `object` refers '
             'to the actual record on which the expression will be executed. '
             'An empty expression will always return `True`.'
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        help='Company related check. If inherited object does not have a '
             '`company_id` field, it will be ignored. '
             'The check will first take the records with a company then, '
             'if no match is found, the ones without a company.'
    )

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the standard image, limited to 1024x1024px"
    )
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views."
    )
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required."
    )

    @api.model
    def _process_images(self, vals, required=False):
        if set(['image', 'image_medium', 'image_small']) & set(vals.keys()):
            tools.image_resize_images(vals)
        elif required:
            raise ValidationError(
                _('At least one image type must be specified')
            )

    @api.model
    def create(self, vals):
        self._process_images(vals, required=True)
        return super().create(vals)

    @api.multi
    def write(self, vals):
        self._process_images(vals)
        return super().write(vals)
