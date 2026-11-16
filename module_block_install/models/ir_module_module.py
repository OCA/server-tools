# Copyright 2026 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import ipaddress
import logging
from configparser import ConfigParser

from odoo import models
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import config
from odoo.tools.misc import str2bool

from ..hooks import borrowed_request

_logger = logging.getLogger(__name__)

CONFIG_SECTION = "module_block_install"


def _get_config():
    """Read the ``[module_block_install]`` section of the server configuration.

    A section of its own, and not ``[options]``: since 19.0, Odoo warns about
    every option of ``[options]`` it does not declare itself, and the config
    file is parsed before addons are imported, so they cannot declare theirs.

    Read from the configuration on purpose, and never from
    ``ir.config_parameter``: the administrator being blocked could change that.
    With ``server_environment`` installed, its configuration is used instead.
    """
    try:
        from odoo.addons.server_environment import serv_config
    except ImportError:
        serv_config = None
    if serv_config is not None:
        if serv_config.has_section(CONFIG_SECTION):
            return dict(serv_config[CONFIG_SECTION])
        return {}
    cfg_path = config.get("config")
    if not cfg_path:
        return {}
    parser = ConfigParser(interpolation=None)
    parser.read(cfg_path)
    if parser.has_section(CONFIG_SECTION):
        return dict(parser[CONFIG_SECTION])
    return {}


def _is_blocking_enabled():
    """``enabled``: on by default."""
    value = _get_config().get("enabled", True)
    if isinstance(value, str):
        return str2bool(value.strip(), True)
    return bool(value)


def _get_allowed_networks():
    """Parse ``allowed_ips``: a comma-separated list of IP addresses or
    networks (CIDR notation)."""
    value = _get_config().get("allowed_ips") or ""
    if isinstance(value, str):
        value = value.split(",")
    networks = []
    for item in value:
        item = item.strip()
        if not item:
            continue
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            _logger.warning(
                "module_block_install: ignoring invalid allowed IP %r", item
            )
    return networks


def _get_http_request():
    """The HTTP request being served, if any.

    ``odoo.http.request`` is unbound while ``dispatch_rpc`` runs an
    ``/xmlrpc`` or ``/jsonrpc`` call: fall back on the request it borrowed.
    """
    if request:
        return request
    return borrowed_request.get()


def _is_allowed_address(remote_addr):
    if not remote_addr:
        return False
    try:
        address = ipaddress.ip_address(remote_addr)
    except ValueError:
        return False
    return any(address in network for network in _get_allowed_networks())


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    def _module_block_install_message(self, operation, module_names):
        names = ", ".join(module_names) or self.env._("(none)")
        if operation == "install":
            return self.env._(
                "Module installation is disabled on this database. "
                "The following modules were not installed: %(modules)s.\n"
                "Ask your Odoo partner to add them to the project and deploy "
                "them.\n"
                "If you were saving settings, the other changes saved at the "
                "same time have not been applied either.",
                modules=names,
            )
        if operation == "upgrade":
            return self.env._(
                "Module upgrade is disabled on this database. "
                "The following modules were not upgraded: %(modules)s.\n"
                "Ask your Odoo partner to deploy the upgrade.",
                modules=names,
            )
        if operation == "uninstall":
            return self.env._(
                "Module uninstallation is disabled on this database. "
                "The following modules were not uninstalled: %(modules)s.\n"
                "Ask your Odoo partner to remove them from the project and "
                "deploy the change.",
                modules=names,
            )
        return self.env._(
            "Module operations are disabled on this database. "
            "The following modules were not processed: %(modules)s.\n"
            "Ask your Odoo partner to deploy the change.",
            modules=names,
        )

    def _module_block_install_check(self, operation, method_name, modules=None):
        """Refuse a module operation when it runs inside an HTTP request.

        Calls made outside an HTTP request (``odoo -i/-u``,
        ``click-odoo-update``, ``odoo shell``, server-side scripts) are let
        through, as are requests coming from an allowed IP address.

        :param str operation: ``install``, ``upgrade``, ``uninstall`` or
            ``apply``; only used to pick the error message.
        :param str method_name: guarded method, for the log line.
        :param modules: the ``ir.module.module`` records concerned; defaults
            to ``self``.
        """
        http_request = _get_http_request()
        if not http_request or not _is_blocking_enabled():
            return
        remote_addr = http_request.httprequest.remote_addr
        if _is_allowed_address(remote_addr):
            return
        if modules is None:
            modules = self
        module_names = modules.sudo().mapped("name")
        user = self.env.user
        _logger.warning(
            "BLOCK access to module.%s on %s to user %s #%s via %s",
            method_name,
            module_names,
            user.login,
            user.id,
            remote_addr,
        )
        raise UserError(self._module_block_install_message(operation, module_names))

    # Install

    def button_install(self):
        self._module_block_install_check("install", "button_install")
        return super().button_install()

    def button_immediate_install(self):
        self._module_block_install_check("install", "button_immediate_install")
        return super().button_immediate_install()

    # Upgrade

    def button_upgrade(self):
        self._module_block_install_check("upgrade", "button_upgrade")
        return super().button_upgrade()

    def button_immediate_upgrade(self):
        self._module_block_install_check("upgrade", "button_immediate_upgrade")
        return super().button_immediate_upgrade()

    # Uninstall

    def button_uninstall(self):
        self._module_block_install_check("uninstall", "button_uninstall")
        return super().button_uninstall()

    def button_immediate_uninstall(self):
        self._module_block_install_check("uninstall", "button_immediate_uninstall")
        return super().button_immediate_uninstall()

    def button_uninstall_wizard(self):
        self._module_block_install_check("uninstall", "button_uninstall_wizard")
        return super().button_uninstall_wizard()

    def module_uninstall(self):
        self._module_block_install_check("uninstall", "module_uninstall")
        return super().module_uninstall()
