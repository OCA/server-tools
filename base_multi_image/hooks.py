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


def pre_init_hook(cr):
    """run the migration for product_images"""
    migrate_from_product_images(cr)


def migrate_from_product_images(cr):
    """If we're installed on a database which has product_images from 7,
    move its table so that we use the already existing images"""
    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'product_images'")
    if not cr.fetchone():
        return
    cr.execute(
        'alter table product_images rename to base_multi_image_image')
    cr.execute(
        'alter table base_multi_image_image rename product_id to owner_id')
    cr.execute(
        'alter table base_multi_image_image '
        "add column owner_model varchar not null default 'product.template',"
        "add column storage varchar not null default 'db'")
    cr.execute(
        'alter table base_multi_image_image '
        'alter column owner_model drop default')
    # we assume all images apply to all variants
    cr.execute(
        "update base_multi_image_image set "
        "owner_id=p.product_tmpl_id "
        "from product_product p where p.id=owner_id"
    )
    # and there might be dangling links
    cr.execute('delete from base_multi_image_image where owner_id is null')
