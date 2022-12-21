# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from openupgradelib.openupgrade import rename_fields, rename_models, rename_tables

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Migrating 'image' model to 'conditional.image'")
    rename_models(cr, [("image", "conditional.image")])
    rename_tables(cr, [("image", "conditional_image")])
    # Only migrate field image to image_1920 (as it's the 'base' field) and
    # image_medium to image_128 (as they are supposed to be the same size).
    # Other fields are related to image_1920 and will have to be recomputed
    _logger.info("Migrating 'conditional.image' attachment fields")
    env = api.Environment(cr, SUPERUSER_ID, {})
    rename_fields(
        env,
        [
            ("conditional.image", "conditional_image", "image", "image_1920"),
            ("conditional.image", "conditional_image", "image_medium", "image_128"),
        ],
    )
    # Delete attachments for image_small (originally 64px)
    # as image_256, image_512 and image_1024 will have to be recomputed
    conditional_image_small_attachments = env["ir.attachment"].search(
        [("res_model", "=", "conditional.image"), ("res_field", "=", "image_small")]
    )
    if conditional_image_small_attachments:
        conditional_image_small_attachments.unlink()
    _logger.warning(
        "Please run 'Resize conditional images' ir.cron to generate missing image sizes"
    )
