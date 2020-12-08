# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# flake8: noqa: C901

import logging
import os

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.modules import get_module_path
from odoo.tools import config
from odoo.tools.translate import _

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
        readonly=True,
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
            if float(self.config_id.version) < 14:
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
                return (
                    "ERROR: no upgrade_path set when writing analysis of %s\n"
                    % module_name
                )
            full_path = os.path.join(self.upgrade_path, module_name, version)
        else:
            full_path = os.path.join(
                get_module_path(module_name, "migrations", version)
            )
        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
            except os.error:
                return "ERROR: could not create migrations directory %s:\n" % (
                    full_path
                )
        logfile = os.path.join(full_path, filename)
        try:
            f = open(logfile, "w")
        except Exception:
            return "ERROR: could not open file %s for writing:\n" % logfile
        _logger.debug("Writing analysis to %s", logfile)
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
                from odoo.addons.openupgrade_scripts import apriori
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

        for ignore_module in _IGNORE_MODULES:
            if ignore_module in keys:
                keys.remove(ignore_module)

        for key in keys:
            contents = "---Models in module '%s'---\n" % key
            if key in res_model:
                contents += "\n".join([str(line) for line in res_model[key]])
                if res_model[key]:
                    contents += "\n"
            contents += "---Fields in module '%s'---\n" % key
            if key in res:
                contents += "\n".join([str(line) for line in sorted(res[key])])
                if res[key]:
                    contents += "\n"
            contents += "---XML records in module '%s'---\n" % key
            if key in res_xml:
                contents += "\n".join([str(line) for line in res_xml[key]])
                if res_xml[key]:
                    contents += "\n"
            if key not in res and key not in res_xml and key not in res_model:
                contents += "---nothing has changed in this module--\n"
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
        self.write(
            {
                "state": "done",
                "log": general_log,
            }
        )
        return True
