# -*- coding: utf-8 -*-
# © 2016 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook_for_submodules(cr, registry, model, field):
    """Moves images from single to multi mode.

    Feel free to use this as a ``post_init_hook`` for submodules.

    :param str model:
        Model name, like ``product.template``.

    :param str field:
        Binary field that had the images in that :param:`model`, like
        ``image``.
    """
    with cr.savepoint():
        records = registry[model].search(
            cr,
            SUPERUSER_ID,
            [(field, "!=", False)],
            context=dict())

        _logger.info("Moving images from %s to multi image mode.", model)
        for r in registry[model].browse(cr, SUPERUSER_ID, records):
            _logger.debug("Setting up multi image for record %d.", r.id)
            r.image_main = r[field]
