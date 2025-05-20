# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016-2020 Opener B.V. <https://opener.am>
# Copyright 2019 ForgeFlow <https://forgeflow.com>
# Copyright 2020 GRAP <https://grap.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# flake8: noqa: C901

import logging
import os
from copy import deepcopy

from lxml import etree

from odoo import fields, models, release
from odoo.exceptions import ValidationError
from odoo.modules import get_module_path
from odoo.tools import config
from odoo.tools.convert import nodeattr2bool
from odoo.tools.translate import _

try:
    from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules
except ImportError:
    renamed_modules = {}
    merged_modules = {}

from .. import compare

_logger = logging.getLogger(__name__)
_IGNORE_MODULES = ["openupgrade_records", "upgrade_analysis"]


class UpgradeAnalysis(models.Model):
    _name = "upgrade.analysis"
    _description = "Upgrade Analyses"

    analysis_date = fields.Datetime(readonly=True)

    state = fields.Selection(
        [("draft", "draft"), ("done", "Done")], readonly=True, default="draft"
    )
    config_id = fields.Many2one(
        string="Comparison Config",
        comodel_name="upgrade.comparison.config",
        readonly=True,
        required=True,
    )

    log = fields.Text(readonly=True)
    upgrade_path = fields.Char(
        compute="_compute_upgrade_path",
        readonly=False,
        store=True,
        help=(
            "The base file path to save the analyse files of Odoo modules. "
            "Taken from Odoo's --upgrade-path command line option or the "
            "'scripts' subdirectory in the openupgrade_scripts addon."
        ),
    )
    write_files = fields.Boolean(
        help="Write analysis files to the module directories", default=True
    )

    def _compute_upgrade_path(self):
        """Return the --upgrade-path configuration option or the `scripts`
        directory in `openupgrade_scripts` if available
        """
        res = config.get("upgrade_path", False)
        if not res:
            module_path = get_module_path("openupgrade_scripts", display_warning=False)
            if module_path:
                res = os.path.join(module_path, "scripts")
        self.upgrade_path = res

    def _get_remote_model(self, connection, model):
        self.ensure_one()
        if model == "record":
            if float(self.config_id.version) < 14.0:
                return connection.env["openupgrade.record"]
            else:
                return connection.env["upgrade.record"]
        return False

    def _write_file(
        self, module_name, version, content, filename="upgrade_analysis.txt"
    ):
        module = self.env["ir.module.module"].search([("name", "=", module_name)])[0]
        if module.is_odoo_module:
            if not self.upgrade_path:
                self._compute_upgrade_path()
                if not self.upgrade_path:
                    return (
                        f"ERROR: no upgrade_path set when writing analysis of "
                        f"{module_name}\n"
                    )
            full_path = os.path.join(self.upgrade_path, module_name, version)
        else:
            full_path = os.path.join(
                get_module_path(module_name), "migrations", version
            )
        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
            except OSError:
                return f"ERROR: could not create migrations directory {full_path}:\n"
        logfile = os.path.join(full_path, filename)
        try:
            f = open(logfile, "w")
        except Exception:
            return f"ERROR: could not open file {logfile} for writing:\n"
        _logger.debug(f"Writing analysis to {logfile}")
        f.write(content)
        f.close()
        return None

    def analyze(self):
        """
        Retrieve both sets of database representations,
        perform the comparison and register the resulting
        change set
        """
        self.ensure_one()
        self.write(
            {
                "analysis_date": fields.Datetime.now(),
            }
        )

        connection = self.config_id.get_connection()
        RemoteRecord = self._get_remote_model(connection, "record")
        LocalRecord = self.env["upgrade.record"]

        # Retrieve field representations and compare
        remote_records = RemoteRecord.field_dump()
        local_records = LocalRecord.field_dump()
        res = compare.compare_sets(remote_records, local_records)

        # Retrieve xml id representations and compare
        flds = [
            "module",
            "model",
            "name",
            "noupdate",
            "prefix",
            "suffix",
            "domain",
            "definition",
        ]
        local_xml_records = [
            {field: record[field] for field in flds}
            for record in LocalRecord.search([("type", "=", "xmlid")])
        ]
        remote_xml_record_ids = RemoteRecord.search([("type", "=", "xmlid")])
        remote_xml_records = [
            {field: record[field] for field in flds}
            for record in RemoteRecord.read(remote_xml_record_ids, flds)
        ]
        res_xml = compare.compare_xml_sets(remote_xml_records, local_xml_records)

        # Retrieve model representations and compare
        flds = [
            "module",
            "model",
            "name",
            "model_original_module",
            "model_type",
        ]
        local_model_records = [
            {field: record[field] for field in flds}
            for record in LocalRecord.search([("type", "=", "model")])
        ]
        remote_model_record_ids = RemoteRecord.search([("type", "=", "model")])
        remote_model_records = [
            {field: record[field] for field in flds}
            for record in RemoteRecord.read(remote_model_record_ids, flds)
        ]
        res_model = compare.compare_model_sets(
            remote_model_records, local_model_records
        )

        affected_modules = sorted(
            {
                record["module"]
                for record in remote_records
                + local_records
                + remote_xml_records
                + local_xml_records
                + remote_model_records
                + local_model_records
            }
        )
        if "base" in affected_modules:
            try:
                pass
            except ImportError:
                _logger.error(
                    "You are using upgrade_analysis on core modules without "
                    " having openupgrade_scripts module available."
                    " The analysis process will not work properly,"
                    " if you are generating analysis for the odoo modules"
                    " in an openupgrade context."
                )

        # reorder and output the result
        keys = ["general"] + affected_modules
        modules = {
            module["name"]: module
            for module in self.env["ir.module.module"].search(
                [("state", "=", "installed")]
            )
        }
        general_log = ""

        no_changes_modules = []

        for ignore_module in _IGNORE_MODULES:
            if ignore_module in keys:
                keys.remove(ignore_module)

        for key in keys:
            contents = f"---Models in module '{key}'---\n"
            if key in res_model:
                contents += "\n".join([str(line) for line in res_model[key]])
                if res_model[key]:
                    contents += "\n"
            contents += f"---Fields in module '{key}'---\n"
            if key in res:
                contents += "\n".join([str(line) for line in sorted(res[key])])
                if res[key]:
                    contents += "\n"
            contents += f"---XML records in module '{key}'---\n"
            if key in res_xml:
                contents += "\n".join([str(line) for line in res_xml[key]])
                if res_xml[key]:
                    contents += "\n"
            if key not in res and key not in res_xml and key not in res_model:
                contents += "---nothing has changed in this module--\n"
                no_changes_modules.append(key)
            if key == "general":
                general_log += contents
                continue
            if compare.module_map(key) not in modules:
                general_log += (
                    "ERROR: module not in list of installed modules:\n" + contents
                )
                continue
            if key not in modules:
                # no need to log in full log the merged/renamed modules
                continue
            if self.write_files:
                error = self._write_file(key, modules[key].installed_version, contents)
                if error:
                    general_log += error
                    general_log += contents
            else:
                general_log += contents

        # Store the full log
        if self.write_files and "base" in modules:
            self._write_file(
                "base",
                modules["base"].installed_version,
                general_log,
                "upgrade_general_log.txt",
            )

        try:
            self.generate_noupdate_changes()
        except Exception as e:
            _logger.exception(f"Error generating noupdate changes: {e}")
            general_log += "ERROR: error when generating noupdate changes: {e}\n"
        try:
            self.generate_module_coverage_file(no_changes_modules)
        except Exception as e:
            _logger.exception(f"Error generating module coverage file: {e}")
            general_log += f"ERROR: error when generating module coverage file: {e}\n"

        self.write(
            {
                "state": "done",
                "log": general_log,
            }
        )
        return True

    @staticmethod
    def _get_node_dict(element):
        res = {}
        if element is None:
            return res
        for child in element:
            if "name" in child.attrib:
                key = "./{}[@name='{}']".format(child.tag, child.attrib["name"])
                res[key] = child
        return res

    @staticmethod
    def _get_node_value(element):
        if "eval" in element.attrib.keys():
            return element.attrib["eval"]
        if "ref" in element.attrib.keys():
            return element.attrib["ref"]
        if not len(element):
            return element.text
        return etree.tostring(element)

    def _get_xml_diff(
        self, remote_update, remote_noupdate, local_update, local_noupdate
    ):
        odoo = etree.Element("odoo")
        for xml_id in sorted(local_noupdate.keys()):
            local_record = local_noupdate[xml_id]
            remote_record = None
            if xml_id in remote_update and xml_id not in remote_noupdate:
                remote_record = remote_update[xml_id]
            elif xml_id in remote_noupdate:
                remote_record = remote_noupdate[xml_id]

            if "." in xml_id:
                module_xmlid = xml_id.split(".", 1)[0]
            else:
                module_xmlid = ""

            if remote_record is None and not module_xmlid:
                continue

            if local_record.tag == "template":
                old_tmpl = etree.tostring(remote_record, encoding="utf-8")
                new_tmpl = etree.tostring(local_record, encoding="utf-8")
                if old_tmpl != new_tmpl:
                    odoo.append(local_record)
                continue

            element = etree.Element(
                "record", id=xml_id, model=local_record.attrib["model"]
            )
            # Add forcecreate attribute if exists
            if local_record.attrib.get("forcecreate"):
                element.attrib["forcecreate"] = local_record.attrib["forcecreate"]
            record_remote_dict = self._get_node_dict(remote_record)
            record_local_dict = self._get_node_dict(local_record)
            for key in sorted(record_remote_dict.keys()):
                if not local_record.xpath(key):
                    # The element is no longer present.
                    # Does the field still exist?
                    if record_remote_dict[key].tag == "field":
                        field_name = remote_record.xpath(key)[0].attrib.get("name")
                        if (
                            field_name
                            not in self.env[local_record.attrib["model"]]._fields.keys()
                        ):
                            continue
                    # Overwrite an existing value with an empty one.
                    attribs = deepcopy(record_remote_dict[key]).attrib
                    for attr in ["eval", "ref"]:
                        if attr in attribs:
                            del attribs[attr]
                    element.append(etree.Element(record_remote_dict[key].tag, attribs))
                else:
                    oldrepr = self._get_node_value(record_remote_dict[key])
                    newrepr = self._get_node_value(record_local_dict[key])

                    if oldrepr != newrepr:
                        element.append(deepcopy(record_local_dict[key]))

            for key in sorted(record_local_dict.keys()):
                if remote_record is None or not remote_record.xpath(key):
                    element.append(deepcopy(record_local_dict[key]))

            if len(element):
                odoo.append(element)

        if not len(odoo):
            return ""
        return etree.tostring(
            etree.ElementTree(odoo),
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        ).decode("utf-8")

    @staticmethod
    def _update_node(target, source):
        for element in source:
            if "name" in element.attrib:
                query = "./{}[@name='{}']".format(element.tag, element.attrib["name"])
            else:
                # query = "./{}".format(element.tag)
                continue
            for existing in target.xpath(query):
                target.remove(existing)
            target.append(element)

    @classmethod
    def _process_data_node(
        self, data_node, records_update, records_noupdate, module_name
    ):
        noupdate = nodeattr2bool(data_node, "noupdate", False)
        for record in data_node.xpath("./record") + data_node.xpath("./template"):
            self._process_record_node(
                record, noupdate, records_update, records_noupdate, module_name
            )

    @classmethod
    def _process_record_node(
        self, record, noupdate, records_update, records_noupdate, module_name
    ):
        xml_id = record.get("id")
        if not xml_id:
            return
        if "." in xml_id and xml_id.startswith(module_name + "."):
            xml_id = xml_id[len(module_name) + 1 :]
        for records in records_noupdate, records_update:
            # records can occur multiple times in the same module
            # with different noupdate settings
            if xml_id in records:
                # merge records (overwriting an existing element
                # with the same tag). The order processing the
                # various directives from the manifest is
                # important here
                self._update_node(records[xml_id], record)
                break
        else:
            target_dict = records_noupdate if noupdate else records_update
            target_dict[xml_id] = record

    @classmethod
    def _parse_files(self, xml_files, module_name):
        records_update = {}
        records_noupdate = {}
        parser = etree.XMLParser(
            remove_blank_text=True,
            strip_cdata=False,
        )
        for xml_file in xml_files:
            try:
                # This is for a final correct pretty print
                # Ref.: https://stackoverflow.com/a/7904066
                # Also don't strip CDATA tags as needed for HTML content
                root_node = etree.fromstring(xml_file.encode("utf-8"), parser=parser)
            except etree.XMLSyntaxError:
                continue
            # Support xml files with root Element either odoo or openerp
            # Condition: each xml file should have only one root element
            # {<odoo>, <openerp> or —rarely— <data>};
            root_node_noupdate = nodeattr2bool(root_node, "noupdate", False)
            if root_node.tag not in ("openerp", "odoo", "data"):
                raise ValidationError(
                    _("Unexpected root Element: %(root)s in file: %(file)s")
                    % {"root": root_node.getroot(), "file": xml_file}
                )
            for node in root_node:
                if node.tag == "data":
                    self._process_data_node(
                        node, records_update, records_noupdate, module_name
                    )
                elif node.tag == "record":
                    self._process_record_node(
                        node,
                        root_node_noupdate,
                        records_update,
                        records_noupdate,
                        module_name,
                    )

        return records_update, records_noupdate

    def generate_noupdate_changes(self):
        """Communicate with the remote server to fetch all xml data records
        per module, and generate a diff in XML format that can be imported
        from the module's migration script using openupgrade.load_data()
        """
        self.ensure_one()
        connection = self.config_id.get_connection()
        remote_record_obj = self._get_remote_model(connection, "record")
        local_record_obj = self.env["upgrade.record"]
        local_modules = local_record_obj.list_modules()
        all_remote_modules = remote_record_obj.list_modules()
        for local_module in local_modules:
            remote_files = []
            remote_modules = []
            remote_update, remote_noupdate = {}, {}
            for remote_module in all_remote_modules:
                if local_module == renamed_modules.get(
                    remote_module, merged_modules.get(remote_module, remote_module)
                ):
                    remote_files.extend(
                        remote_record_obj.get_xml_records(remote_module)
                    )
                    remote_modules.append(remote_module)
                    add_remote_update, add_remote_noupdate = self._parse_files(
                        remote_files, remote_module
                    )
                    remote_update.update(add_remote_update)
                    remote_noupdate.update(add_remote_noupdate)
            if not remote_modules:
                continue
            local_files = local_record_obj.get_xml_records(local_module)
            local_update, local_noupdate = self._parse_files(local_files, local_module)
            diff = self._get_xml_diff(
                remote_update, remote_noupdate, local_update, local_noupdate
            )
            if diff:
                module = self.env["ir.module.module"].search(
                    [("name", "=", local_module)]
                )
                self._write_file(
                    local_module,
                    module.installed_version,
                    diff,
                    filename="noupdate_changes.xml",
                )
        return True

    def generate_module_coverage_file(self, no_changes_modules):
        self.ensure_one()

        module_coverage_file_folder = config.get("module_coverage_file_folder", False)

        if not module_coverage_file_folder:
            return

        module_domain = [
            ("state", "=", "installed"),
            (
                "name",
                "not in",
                [
                    "upgrade_analysis",
                    "openupgrade_records",
                    "openupgrade_scripts",
                    "openupgrade_framework",
                ],
            ),
        ]

        connection = self.config_id.get_connection()
        all_local_modules = (
            self.env["ir.module.module"].search(module_domain).mapped("name")
        )

        all_remote_modules = [
            x["name"]
            for x in connection.env["ir.module.module"].search_read(
                module_domain, ["name"]
            )
        ]

        start_version = connection.version
        end_version = release.major_version
        module_width = 51
        description_width = 49

        all_modules = sorted(list(set(all_remote_modules + all_local_modules)))
        module_descriptions = {}
        for module in all_modules:
            status = ""
            is_new = False
            if module in all_local_modules and module in all_remote_modules:
                module_description = f" {module}"
            elif module in all_local_modules:
                module_description = f" |new| {module}"
                is_new = True
            else:
                module_description = f" |del| {module}"

            # new modules cannot be merged/renamed in same version
            if not is_new and module in compare.apriori.merged_modules:
                status = f"Merged into {compare.apriori.merged_modules[module]}. "
            elif not is_new and module in compare.apriori.renamed_modules:
                status = f"Renamed to {compare.apriori.renamed_modules[module]}. "
            elif module in compare.apriori.renamed_modules.values():
                status = "Renamed from {}. ".format(
                    [
                        x
                        for x in compare.apriori.renamed_modules
                        if compare.apriori.renamed_modules[x] == module
                    ][0]
                )
            elif module in no_changes_modules:
                status += "No DB layout changes. "
            module_descriptions[
                module_description.ljust(module_width, " ")[0 : module_width - 1] + " "
            ] = status.ljust(description_width, " ")[0 : description_width - 1] + " "

        rendered_text = self.env["ir.qweb"]._render(
            "upgrade_analysis.module_coverage",
            values=dict(
                start_version=start_version,
                end_version=end_version,
                module_descriptions=module_descriptions,
            ),
        )

        file_name = "modules{}-{}.rst".format(
            start_version.replace(".", ""),
            end_version.replace(".", ""),
        )

        file_path = os.path.join(module_coverage_file_folder, file_name)
        f = open(file_path, "w+")
        f.write(rendered_text)
        f.close()
        return True
