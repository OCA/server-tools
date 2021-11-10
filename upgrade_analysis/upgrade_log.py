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


def isfunction(model, k):
    if (
        model._fields[k].compute
        and not model._fields[k].related
        and not model._fields[k].company_dependent
    ):
        return "function"
    return ""


def isproperty(model, k):
    if model._fields[k].company_dependent:
        return "property"
    return ""


def isrelated(model, k):
    if model._fields[k].related:
        return "related"
    return ""


def _get_relation(v):
    if v.type in ("many2many", "many2one", "one2many"):
        return v.comodel_name
    elif v.type == "many2one_reference":
        return v.model_field
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
    for k, v in model._fields.items():
        properties = {
            "type": typemap.get(v.type, v.type),
            "isfunction": isfunction(model, k),
            "isproperty": isproperty(model, k),
            "isrelated": isrelated(model, k),
            "relation": _get_relation(v),
            "table": v.relation if v.type == "many2many" else "",
            "required": v.required and "required" or "",
            "stored": v.store and "stored" or "",
            "selection_keys": "",
            "req_default": "",
            "hasdefault": model._fields[k].default and "hasdefault" or "",
        }
        if v.type == "selection":
            if isinstance(v.selection, (tuple, list)):
                properties["selection_keys"] = str(sorted(x[0] for x in v.selection))
            else:
                properties["selection_keys"] = "function"
        elif v.type == "binary":
            properties["attachment"] = str(getattr(v, "attachment", False))
        default = model._fields[k].default
        if v.required and default:
            if (
                callable(default)
                or isinstance(default, str)
                and getattr(model._fields[k], default, False)
                and callable(getattr(model._fields[k], default))
            ):
                properties["req_default"] = "function"
            else:
                properties["req_default"] = str(default)
        for key, value in properties.items():
            if value:
                model_registry.setdefault(k, {})[key] = value


def log_xml_id(cr, module, xml_id):
    """
    Log xml_ids at load time in the records table.
    Called from tools/convert.py:xml_import._test_xml_id()

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
