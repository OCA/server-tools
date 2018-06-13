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
    env = api.Environment(cr, SUPERUSER_ID, {})
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


def uninstall_hook_for_submodules(cr, registry, model, field=None, field_medium=None, field_small=None):
    """Moves images from multi to single mode and remove multi-images for a given model.

    :param odoo.sql_db.Cursor cr:
        Database cursor.

    :param odoo.modules.registry.RegistryManager registry:
        Database registry, using v7 api.

    :param str model:
        Model technical name, like "res.partner". All multi-images for that
        model will be deleted
    
    :param str field:
        Binary field that had the images in that :param:`model`, like
        ``image``.
    
    :param str field_medium:
        Binary field that had the medium-sized images in that :param:`model`, like
        ``image_medium``.
    
    :param str field_small:
        Binary field that had the small-sized images in that :param:`model`, like
        ``image_small``.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    with cr.savepoint():
        Image = env["base_multi_image.image"]
        images = Image.search([("owner_model", "=", model)], order="sequence, id")
        if images and (field or field_medium or field_small):
            main_images = {}
            for image in images:
                if image.owner_id not in main_images:
                    main_images[image.owner_id] = image
            main_images = main_images.values()
            Model = env[model]
            Field = field and Model._fields[field]
            FieldMedium = field_medium and Model._fields[field_medium]
            FieldSmall = field_small and Model._fields[field_small]
            # fields.Binary(), save the binary content directly to the table
            if field and not Field.attachment \
            or field_medium and not FieldMedium.attachment \
            or field_small and not FieldSmall.attachment:
                fields = []
                if field and not Field.attachment:
                    fields.append(field + " = " + "%(image)s")
                if field_medium and not FieldMedium.attachment:
                    fields.append(field_medium + " = " + "%(image_medium)s")
                if field_small and not FieldSmall.attachment:
                    fields.append(field_small + " = " + "%(image_small)s")
                query = """
                    UPDATE %(table)s
                    SET %(fields)s
                    WHERE id = %%(id)s
                """ % {
                    "table": Model._table,
                    "fields": ", ".join(fields),
                }
                for main_image in main_images:
                    vars = {"id": main_image.owner_id}
                    if field and not Field.attachment:
                        vars["image"] = main_image.image_main
                    if field_medium and not FieldMedium.attachment:
                        vars["image_medium"] = main_image.image_medium
                    if field_small and not FieldSmall.attachment:
                        vars["image_small"] = main_image.image_small
                    cr.execute(query, vars)
            # fields.Binary(attachment=True), save the ir_attachment record ID
            if field and Field.attachment \
            or field_medium and FieldMedium.attachment \
            or field_small and FieldSmall.attachment:
                for main_image in main_images:
                    owner = Model.browse(main_image.owner_id)
                    if field and Field.attachment:
                        Field.write(owner, main_image.image_main)
                    if field_medium and FieldMedium.attachment:
                        FieldMedium.write(owner, main_image.image_medium)
                    if field_small and FieldSmall.attachment:
                        FieldSmall.write(owner, main_image.image_small)
        images.unlink()


def table_has_column(cr, table, field):
    query = """
        SELECT %(field)s
        FROM information_schema.columns
        WHERE table_name=%(table)s and column_name=%(field)s;
    """
    cr.execute(query, {'table': table, 'field': field})
    return bool(cr.fetchall())
