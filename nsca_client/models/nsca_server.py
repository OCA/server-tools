# (Copyright) 2015 ABF OSIELL <http://osiell.com>
# (Copyright) 2018 Creu Blanca
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import errno
import logging
import os
import shlex
import subprocess

import psutil

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


_logger = logging.getLogger(__name__)

SEND_NSCA_BIN = "/usr/sbin/send_nsca"


class NscaServer(models.Model):
    _name = "nsca.server"
    _description = "NSCA Server"

    name = fields.Char("Hostname", required=True)
    port = fields.Integer("Port", default=5667, required=True)
    password = fields.Char("Password")
    encryption_method = fields.Selection(
        selection="_selection_encryption_method",
        string="Encryption method",
        default="1",
        required=True,
    )
    config_dir_path = fields.Char(
        "Configuration directory", compute="_compute_config_dir_path"
    )
    config_file_path = fields.Char(
        "Configuration file", compute="_compute_config_file_path"
    )
    node_hostname = fields.Char(
        "Hostname of this node",
        required=True,
        help="This is the hostname of the current Odoo node declared in the "
        "monitoring server.",
    )
    check_ids = fields.One2many("nsca.check", "server_id", string="Checks")
    check_count = fields.Integer(compute="_compute_check_count")

    @api.depends("check_ids")
    def _compute_check_count(self):
        for r in self:
            r.check_count = len(r.check_ids)

    def _selection_encryption_method(self):
        return [
            ("0", "0 - None (Do NOT use this option)"),
            ("1", "1 - Simple XOR"),
            ("2", "2 - DES"),
            ("3", "3 - 3DES (Triple DES)"),
            ("4", "4 - CAST-128"),
            ("5", "5 - CAST-256"),
            ("6", "6 - xTEA"),
            ("7", "7 - 3WAY"),
            ("8", "8 - BLOWFISH"),
            ("9", "9 - TWOFISH"),
            ("10", "10 - LOKI97"),
            ("11", "11 - RC2"),
            ("12", "12 - ARCFOUR"),
            ("14", "14 - RIJNDAEL-128"),
            ("15", "15 - RIJNDAEL-192"),
            ("16", "16 - RIJNDAEL-256"),
            ("19", "19 - WAKE"),
            ("20", "20 - SERPENT"),
            ("22", "22 - ENIGMA (Unix crypt)"),
            ("23", "23 - GOST"),
            ("24", "24 - SAFER64"),
            ("25", "25 - SAFER128"),
            ("26", "26 - SAFER+"),
        ]

    def _compute_config_dir_path(self):
        for server in self:
            data_dir_path = config.get("data_dir")
            dir_path = os.path.join(data_dir_path, "nsca_client", self.env.cr.dbname)
            server.config_dir_path = dir_path

    def _compute_config_file_path(self):
        for server in self:
            file_name = "send_nsca_%s.cfg" % server.id
            full_path = os.path.join(server.config_dir_path, file_name)
            server.config_file_path = full_path

    def write_config_file(self):
        for server in self:
            try:
                os.makedirs(server.config_dir_path)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
            with open(server.config_file_path, "w") as config_file:
                if server.password:
                    config_file.write("password=%s\n" % server.password)
                config_file.write("encryption_method=%s\n" % server.encryption_method)
        return True

    def write(self, vals):
        res = super(NscaServer, self).write(vals)
        self.write_config_file()
        return res

    @api.model
    def create(self, vals):
        res = super(NscaServer, self).create(vals)
        res.write_config_file()
        return res

    @api.model
    def current_status(self):
        ram = 0
        cpu = 0
        if psutil:
            process = psutil.Process(os.getpid())
            # psutil changed its api through versions
            processes = [process]
            if config.get("workers") and process.parent:  # pragma: no cover
                if callable(process.parent):
                    process = process.parent()
                else:
                    process = process.parent
                if hasattr(process, "children"):
                    processes += process.children(True)
                elif hasattr(process, "get_children"):
                    processes += process.get_children(True)
            for process in processes:
                if hasattr(process, "memory_percent"):
                    ram += process.memory_percent()
                if hasattr(process, "cpu_percent"):
                    cpu += process.cpu_percent(interval=1)
        user_count = 0
        if "bus.presence" in self.env.registry:
            user_count = self.env["bus.presence"].search_count(
                [("status", "=", "online")]
            )
        performance = {
            "cpu": {"value": cpu},
            "ram": {"value": ram},
            "user_count": {"value": user_count},
        }
        return 0, "OK", performance

    def _prepare_command(self):
        """Prepare the shell command used to send the check result
        to the NSCA daemon.
        """
        cmd = "/usr/sbin/send_nsca -H {} -p {} -c {}".format(
            self.name,
            self.port,
            self.config_file_path,
        )
        return shlex.split(cmd)

    @api.model
    def _run_command(self, cmd, check_result):
        """Send the check result through the '/usr/sbin/send_nsca' command."""
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            stdout = proc.communicate(input=check_result)[0]
            _logger.debug("%s: %s", check_result, stdout.strip())
        except Exception as exc:
            _logger.error(exc)

    def _check_send_nsca_command(self):
        """Check if the NSCA client is installed."""
        if not is_exe(SEND_NSCA_BIN):
            raise UserError(
                _(
                    "Command '%s' not found. Please install the NSCA client.\n"
                    "On Debian/Ubuntu: apt-get install nsca-client"
                )
                % (SEND_NSCA_BIN)
            )

    def _format_check_result(self, service, rc, message):
        """Format the check result with tabulations as delimiter."""
        message = message.replace("\t", " ")
        hostname = self.node_hostname
        check_result = "{}\t{}\t{}\t{}".format(hostname, service, rc, message)
        return check_result.encode("utf-8")

    def _send_nsca(self, service, rc, message, performance):
        """Send the result of the check to the NSCA daemon."""
        msg = message
        if len(performance) > 0:
            msg += "| " + "".join(
                [
                    "%s=%s%s;%s;%s;%s;%s"
                    % (
                        key,
                        performance[key]["value"],
                        performance[key].get("uom", ""),
                        performance[key].get("warn", ""),
                        performance[key].get("crit", ""),
                        performance[key].get("min", ""),
                        performance[key].get("max", ""),
                    )
                    for key in sorted(performance)
                ]
            )
        check_result = self._format_check_result(service, rc, msg)
        cmd = self._prepare_command()
        self._run_command(cmd, check_result)

    def show_checks(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "nsca_client.action_nsca_check_tree"
        )
        context = {"default_server_id": self.id}
        result["context"] = context
        result["domain"] = [("server_id", "=", self.id)]
        if len(self.check_ids) == 1:
            res = self.env.ref("nsca_client.view_nsca_check_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.check_ids.id
        return result
