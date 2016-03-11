# -*- coding: utf-8 -*-
# © 2016 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def pre_init_hook_for_submodules(cr, model, field):
    """Moves images from single to multi mode.

    Feel free to use this as a ``pre_init_hook`` for submodules.

    :param str model:
        Model name, like ``product.template``.

    :param str field:
        Binary field that had the images in that :param:`model`, like
        ``image``.
    """
    env = api.Environment(cr, SUPERUSER_ID, dict())
    with cr.savepoint():
        cr.execute(
            """
                INSERT INTO base_multi_image_image (
                    owner_id,
                    owner_model,
                    storage,
                    file_db_store
                )
                SELECT
                    id,
                    %%s,
                    'db',
                    %(field)s
                FROM
                    %(table)s
                WHERE
                    %(field)s IS NOT NULL
            """ % {"table": env[model]._table, "field": field},
            (model,)
        )
