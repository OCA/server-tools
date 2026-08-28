# © 2016 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook_for_submodules(env, model, field):
    """Moves images from single to multi mode.

    Feel free to use this as a ``pre_init_hook`` for submodules.

    :param str model:
        Model name, like ``product.template``.

    :param str field:
        Binary field that had the images in that :param:`model`, like
        ``image``.
    """
    cr = env.cr
    with cr.savepoint():
        table = env[model]._table
        column_exists = table_has_column(cr, table, field)
        # fields.Binary(), extract the binary content directly from the table
        if column_exists:
            extract_query = f"""
                SELECT id, '{model}', '{model},' || id, 'db', {field}
                FROM {table}
                WHERE {field} IS NOT NULL
            """
            image_field = "file_db_store"
        # fields.Binary(attachment=True), get the ir_attachment record ID
        else:
            extract_query = f"""
                SELECT
                    res_id,
                    res_model,
                    CONCAT_WS(',', res_model, res_id),
                    'attachment',
                    id
                FROM ir_attachment
                WHERE res_field='{field}' AND res_model='{model}'
            """
            image_field = "attachment_id"
        cr.execute(  # pylint: disable=sql-injection
            f"""
                INSERT INTO base_multi_image_image (
                    owner_id,
                    owner_model,
                    owner_ref_id,
                    storage,
                    {image_field}
                )
                {extract_query}
            """
        )


def uninstall_hook_for_submodules(env, model, field=None):
    """Moves images from multi to single mode and remove multi-images for a
    given model.

    :param str model:
        Model technical name, like "res.partner". All multi-images for that
        model will be deleted

    :param str field:
        Binary field that had the images in that :param:`model`, like
        ``image``.

    """
    cr = env.cr
    with cr.savepoint():
        Image = env["base_multi_image.image"]
        images = Image.search([("owner_model", "=", model)], order="sequence, id")
        if images and field:
            main_images = {}
            for image in images:
                if image.owner_id not in main_images:
                    main_images[image.owner_id] = image
            main_images = main_images.values()
            Model = env[model]
            Field = Model._fields[field]

            # fields.Binary(), save the binary content directly to the table
            if not Field.attachment:
                save_directly_to_table(
                    cr,
                    Model,
                    field,
                    Field,
                    main_images,
                )
            # fields.Binary(attachment=True), save the ir_attachment record ID
            if Field.attachment:
                for main_image in main_images:
                    owner = Model.browse(main_image.owner_id)
                    Field.write(owner, main_image.image_1920)
        images.unlink()


def save_directly_to_table(cr, Model, field, Field, main_images):
    fields = []
    if field and not Field.attachment:
        fields.append(field + " = " + "%(image)s")

    query = """
        UPDATE {table}
        SET {fields}
        WHERE id = %%(id)s
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
