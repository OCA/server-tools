# © 2016 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook_for_submodules(cr, model, field):
    """Moves images from single to multi mode.

    Feel free to use this as a ``post_init_hook`` for submodules.

    :param odoo.sql_db.Cursor cr:
        Database cursor.

    :param str model:
        Model name, like ``product.template``.

    :param str field:
        Binary field that had the images in that :param:`model`, like
        ``image``.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    table = env[model]._table
    image_obj = env["base_multi_image.image"]
    with cr.savepoint():
        column_exists = table_has_column(cr, table, field)
        if column_exists:
            cr.execute("SELECT id FROM %(table)s WHERE %(field)s IS NOT NULL")
        else:
            cr.execute(
                """
                    SELECT res_id
                    FROM ir_attachment
                    WHERE
                        res_field=%(field)s
                        AND res_model=%(model)s
                """,
                {
                    "field": field,
                    "model": model,
                },
            )
        record_ids = [row[0] for row in cr.fetchall()]
        for record in env[model].browse(record_ids):
            image_obj.create(
                {
                    "owner_id": record.id,
                    "owner_model": model,
                    "owner_ref_id": f"{model},{record.id}",
                    "image_1920": record[field],
                },
            )


def uninstall_hook_for_submodules(cr, model, field=None):
    """Moves images from multi to single mode and remove multi-images for a
    given model.

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
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    with cr.savepoint():
        image_obj = env["base_multi_image.image"]
        images = image_obj.search([("owner_model", "=", model)], order="sequence, id")
        if images and field:
            main_images = {}
            for image in images:
                if image.owner_id not in main_images:
                    main_images[image.owner_id] = image
            main_images = main_images.values()
            model_obj = env[model]
            field_field = model_obj._fields[field]

            # fields.Binary(), save the binary content directly to the table
            if not field_field.attachment:
                save_directly_to_table(
                    cr,
                    model_obj,
                    field,
                    field_field,
                    main_images,
                )
            # fields.Binary(attachment=True), save the ir_attachment record ID
            if field and field_field.attachment:
                for main_image in main_images:
                    owner = model_obj.browse(main_image.owner_id)
                    field_field.write(owner, main_image.image_1920)
        images.unlink()


def save_directly_to_table(cr, Model, field, Field, main_images):
    fields = []
    if field and not Field.attachment:
        fields.append(field + " = " + "%(image)s")
    query = """
        UPDATE {table}
        SET {fields}
        WHERE id = %(id)s
    """.format(table=Model._table, fields=", ".join(fields))
    for main_image in main_images:
        params = {"id": main_image.owner_id}
        if field and not Field.attachment:
            params["image"] = main_image.image_1920
        cr.execute(query, params)  # pylint: disable=sql-injection


def table_has_column(cr, table, field):
    query = """
        SELECT %(field)s
        FROM information_schema.columns
        WHERE table_name=%(table)s and column_name=%(field)s;
    """
    cr.execute(query, {"table": table, "field": field})
    return bool(cr.fetchall())
