# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib.openupgrade_tools import table_exists

from odoo import models

_logger = logging.getLogger(__name__)


def get_record_id(cr, module, model, field, mode):
    """
    OpenUpgrade: get or create the id from the record table matching
    the key parameter values
    """
    cr.execute(
        "SELECT id FROM upgrade_record "
        "WHERE module = %s AND model = %s AND "
        "field = %s AND mode = %s AND type = %s",
        (module, model, field, mode, "field"),
    )
    record = cr.fetchone()
    if record:
        return record[0]
    cr.execute(
        "INSERT INTO upgrade_record "
        "(create_date, module, model, field, mode, type) "
        "VALUES (NOW() AT TIME ZONE 'UTC', %s, %s, %s, %s, %s)",
        (module, model, field, mode, "field"),
    )
    cr.execute(
        "SELECT id FROM upgrade_record "
        "WHERE module = %s AND model = %s AND "
        "field = %s AND mode = %s AND type = %s",
        (module, model, field, mode, "field"),
    )
    return cr.fetchone()[0]


def compare_registries(cr, module, registry, local_registry):
    """
    OpenUpgrade: Compare the local registry with the global registry,
    log any differences and merge the local registry with
    the global one.
    """
    if not table_exists(cr, "upgrade_record"):
        return
    for model, flds in local_registry.items():
        registry.setdefault(model, {})
        for field, attributes in flds.items():
            old_field = registry[model].setdefault(field, {})
            mode = old_field and "modify" or "create"
            record_id = False
            for key, value in attributes.items():
                if key not in old_field or old_field[key] != value:
                    if not record_id:
                        record_id = get_record_id(cr, module, model, field, mode)
                    cr.execute(
                        "SELECT id FROM upgrade_attribute "
                        "WHERE name = %s AND value = %s AND "
                        "record_id = %s",
                        (key, value, record_id),
                    )
                    if not cr.fetchone():
                        cr.execute(
                            "INSERT INTO upgrade_attribute "
                            "(create_date, name, value, record_id) "
                            "VALUES (NOW() AT TIME ZONE 'UTC', %s, %s, %s)",
                            (key, value, record_id),
                        )
                    old_field[key] = value


def hasdefault(field):
    """Return a representation of the field's default method.

    The default method is only meaningful if the field is a regular read/write
    field with a `default` method or a `compute` method.

    Note that Odoo fields accept a literal value as a `default` attribute
    this value is wrapped in a lambda expression in odoo/fields.py:
    https://github.com/odoo/odoo/blob/7eeba9d/odoo/fields.py#L484-L487
    """
    if (
        not field.readonly  # It's not a proper computed field
        and not field.inverse  # It's not a field that delegates their data
        and not isrelated(field)  # It's not an (unstored) related field.
    ):
        if field.default:
            return "default"
        if field.compute:
            return "compute"
    return ""


def isfunction(field):
    if (
        field.compute
        and (field.readonly or field.inverse)
        and not field.related
        and not field.company_dependent
    ):
        return "function"
    return ""


def isproperty(field):
    if field.company_dependent:
        return "property"
    return ""


def isrelated(field):
    if field.related:
        return "related"
    return ""


def _get_relation(field):
    if field.type in ("many2many", "many2one", "one2many"):
        return field.comodel_name
    elif field.type == "many2one_reference":
        return field.model_field
    else:
        return ""


def log_model(model, local_registry):
    """
    OpenUpgrade: Store the characteristics of the BaseModel and its fields
    in the local registry, so that we can compare changes with the
    main registry
    """

    if not model._name:
        return

    typemap = {"monetary": "float"}

    # persistent models only
    if isinstance(model, models.TransientModel):
        return

    model_registry = local_registry.setdefault(model._name, {})
    if model._inherits:
        model_registry["_inherits"] = {"_inherits": str(model._inherits)}
    model_registry["_order"] = {"_order": model._order}
    for fieldname, field in model._fields.items():
        properties = {
            "type": typemap.get(field.type, field.type),
            "isfunction": isfunction(field),
            "isproperty": isproperty(field),
            "isrelated": isrelated(field),
            "relation": _get_relation(field),
            "table": field.relation if field.type == "many2many" else "",
            "required": field.required and "required" or "",
            "stored": field.store and "stored" or "",
            "selection_keys": "",
            "hasdefault": hasdefault(field),
        }
        if field.type == "selection":
            if isinstance(field.selection, (tuple, list)):
                properties["selection_keys"] = str(
                    sorted(x[0] for x in field.selection)
                )
            else:
                properties["selection_keys"] = "function"
        elif field.type == "binary":
            properties["attachment"] = str(getattr(field, "attachment", False))
        for key, value in properties.items():
            if value:
                model_registry.setdefault(fieldname, {})[key] = value


def log_xml_id(cr, module, xml_id):
    """
    Log xml_ids at load time in the records table.
    Called from:
     - tools/convert.py:xml_import._test_xml_id()
     - odoo/models.py:BaseModel._convert_records()
     - odoo/addons/base/models/ir_model.py:IrModelConstraint._reflect_model()

    # Catcha's
    - The module needs to be loaded with 'init', or the calling method
    won't be called. This can be brought about by installing the
    module or updating the 'state' field of the module to 'to install'
    or call the server with '--init <module>' and the database argument.

    - Do you get the right results immediately when installing the module?
    No, sorry. This method retrieves the model from the ir_model_table, but
    when the xml id is encountered for the first time, this method is called
    before the item is present in this table. Therefore, you will not
    get any meaningful results until the *second* time that you 'init'
    the module.

    - The good news is that the upgrade_analysis module that comes
    with this distribution allows you to deal with all of this with
    one click on the menu item Settings -> Customizations ->
    Database Structure -> OpenUpgrade -> Generate Records

    - You cannot reinitialize the modules in your production database
    and expect to keep working on it happily ever after. Do not perform
    this routine on your production database.

    :param module: The module that contains the xml_id
    :param xml_id: the xml_id, with or without 'module.' prefix
    """
    if not table_exists(cr, "upgrade_record"):
        return
    if "." not in xml_id:
        xml_id = "{}.{}".format(module, xml_id)
    cr.execute(
        "SELECT model FROM ir_model_data " "WHERE module = %s AND name = %s",
        xml_id.split("."),
    )
    record = cr.fetchone()
    if not record:
        _logger.warning("Cannot find xml_id %s", xml_id)
        return
    else:
        cr.execute(
            "SELECT id FROM upgrade_record "
            "WHERE module=%s AND model=%s AND name=%s AND type=%s",
            (module, record[0], xml_id, "xmlid"),
        )
        if not cr.fetchone():
            cr.execute(
                "INSERT INTO upgrade_record "
                "(create_date, module, model, name, type) "
                "values(NOW() AT TIME ZONE 'UTC', %s, %s, %s, %s)",
                (module, record[0], xml_id, "xmlid"),
            )
