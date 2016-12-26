# -*- coding: utf-8 -*-
# © 2016 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID
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
        table = env[model]._table
        column_exists = table_has_column(cr, table, field)
        # fields.Binary(), extract the binary content directly from the table
        if column_exists:
            extract_query = """
                SELECT id, '%(model)s', '%(model)s,' || id, 'db', %(field)s
                FROM %(table)s
                WHERE %(field)s IS NOT NULL
            """ % {
                "table": table,
                "field": field,
                "model": model,
            }
            image_field = 'file_db_store'
        # fields.Binary(attachment=True), get the ir_attachment record ID
        else:
            extract_query = """
                SELECT
                    res_id,
                    res_model,
                    CONCAT_WS(',', res_model, res_id),
                    'filestore',
                    id
                FROM ir_attachment
                WHERE res_field='%(field)s' AND res_model='%(model)s'
            """ % {"model": model, "field": field}
            image_field = 'attachment_id'
        cr.execute(
            """
                INSERT INTO base_multi_image_image (
                    owner_id,
                    owner_model,
                    owner_ref_id,
                    storage,
                    %s
                )
                %s
            """ % (image_field, extract_query)
        )


def uninstall_hook_for_submodules(cr, registry, model):
    """Remove multi-images for a given model.

    :param odoo.sql_db.Cursor cr:
        Database cursor.

    :param odoo.modules.registry.RegistryManager registry:
        Database registry, using v7 api.

    :param str model:
        Model technical name, like "res.partner". All multi-images for that
        model will be deleted
    """
    env = api.Environment(cr, SUPERUSER_ID, dict())
    Image = env["base_multi_image.image"]
    images = Image.search([("owner_model", "=", model)])
    images.unlink()


def table_has_column(cr, table, field):
    query = """
        SELECT %(field)s
        FROM information_schema.columns
        WHERE table_name=%(table)s and column_name=%(field)s;
    """
    cr.execute(query, {'table': table, 'field': field})
    return bool(cr.fetchall())
