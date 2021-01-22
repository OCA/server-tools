# © 2020 Acsone (http://www.acsone.eu)
# Nans Lefebvre <nans.lefebvre@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import uuid

from lxml.builder import E
from slugify import slugify

from odoo import api, models, tools

# TODO: collapse export_list, export_fields, etc into one data structure
# (there are too much variables carried around)
export_structure = {  # smth like that
    "export_fields": {},
    "export_list": [],
    "module": None,
}


def keep_field(f):  # TODO
    """We can safely skip non-stored fields.
       For mail it should be an option, but in general these are just annoying fields.
    """
    ignore_type = f.type in ["binary"]
    ignore_modules = f._module in ["mail", "portal"]
    return f.store and not ignore_type and not ignore_modules


class Base(models.AbstractModel):
    _inherit = "base"

    def xmlify(self, export=None, module=None):
        result = []
        export = {self._name: export} if export else {}
        export_fields = {}
        xml_ids = {}
        export_list = [record for record in self]

        for record in self:
            res = self._xmlify_record(
                record, result, export, module, export_fields, xml_ids, export_list
            )
            result.append(res)

        return result

    @api.model
    def _get_export(self, name, export):
        if name not in export:
            domain = [("default_xml_export", "=", True), ("resource", "=", name)]
            default_export = self.env["ir.exports"].search(domain, limit=1)
            export[name] = default_export
        return export[name]

    @api.model
    def _get_export_fields(self, record, export, export_fields, module):
        name = record._name
        if name not in export_fields:
            export = self._get_export(name, export)
            if export:
                field_names = export.export_fields.mapped("name")
            else:
                field_names = set(record._fields.keys())
            field_names = [
                f
                for f in field_names
                if f not in models.MAGIC_COLUMNS and f != "__last_update"
            ]
            to_export = [(f, record._fields[f]) for f in field_names]
            to_export = [(fn, f) for fn, f in to_export if keep_field(f)]

            if module:
                dps = module.upstream_dependencies(exclude_states=["uninstallable"])
                dependencies = dps.mapped("name")
                fields_from = [module.name] + dependencies
                filter_module = lambda f: f._module in fields_from  # noqa
                to_export = [(fn, f) for fn, f in to_export if filter_module(f)]
            export_fields[name] = sorted(to_export)
        return export_fields[name]

    @api.model
    def _needs_export(self, record, export_list):
        # TODO: choose depending on external_id/fields/module
        # i.e. if we get a record that already has an external id,
        # we might do an override to add the fields we are interested in
        return not record.get_xml_id().get(record.id) and record not in export_list

    @api.model
    def _get_xml_id(self, record, xml_ids):
        if record not in xml_ids:
            external_id = record.get_xml_id().get(record.id)
            if external_id:
                xml_ids[record] = external_id
            else:
                salt = str(uuid.uuid4())[:6]
                dn = "display_name"
                name = record[dn] if dn in record._fields else ""
                record_xml_id = "_".join([record._name, name, salt])
                xml_ids[record] = slugify(record_xml_id).replace("-", "_")
        return xml_ids[record]

    @api.model
    def _xmlify_record(
        self, record, result, export, module, export_fields, xml_ids, export_list
    ):
        xml = E.record(id=self._get_xml_id(record, xml_ids), model=record._name)
        fields = self._get_export_fields(record, export, export_fields, module)
        for fname, field in fields:
            field_xml = self._xmlify_field(
                fname,
                field,
                record,
                result,
                export,
                module,
                export_fields,
                xml_ids,
                export_list,
            )
            xml.append(field_xml)
            # TODO breaks nice formatting...
            # comment = etree.Comment("from module {}".format(field._module))
            # comment.tail = '\n'
            # xml.append(comment)
        return xml

    @api.model
    def _xmlify_field(
        self,
        field_name,
        field,
        record,
        result,
        export,
        module,
        export_fields,
        xml_ids,
        export_list,
    ):
        value = record[field_name]
        if not value:
            return E.field(eval="False", name=field_name)
        field_dict = {"name": field_name}
        if field.type in ["many2one", "many2many", "one2many"]:
            for subrecord in value:
                if self._needs_export(subrecord, export_list):
                    export_list.append(subrecord)
                    subrecord_xml = self._xmlify_record(
                        subrecord,
                        result,
                        export,
                        module,
                        export_fields,
                        xml_ids,
                        export_list,
                    )
                    result.append(subrecord_xml)
            if field.type == "many2one":
                field_dict["ref"] = self._get_xml_id(value, xml_ids)
            else:
                ids = [self._get_xml_id(r, xml_ids) for r in value]
                eval_ids = ["ref('{}')".format(i) for i in ids]
                lids = "[" + ", ".join(eval_ids) + "]"
                field_dict["eval"] = "[(6,0," + lids + ")]"
        elif field.type == "boolean":
            field_dict["eval"] = "True"
        elif field.type == "date":
            field_dict["value"] = value.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        elif field.type == "datetime":
            field_dict["value"] = value.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        else:  # TODO: handle all field types (monetary, html, reference, binary...)
            field_dict["value"] = str(value)
        if "value" in field_dict:
            xml_value = str(field_dict.pop("value"))
            return E.field(xml_value, **field_dict)
        else:
            return E.field(**field_dict)
