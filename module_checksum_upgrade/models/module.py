# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
import logging
import os

from openerp import api, models
from openerp.modules.module import get_module_path

_logger = logging.getLogger(__name__)
try:
    from checksumdir import dirhash
except ImportError:
    _logger.debug('Cannot `import checksumdir`.')

PARAM_INSTALLED_CHECKSUMS = \
    'module_checksum_upgrade.installed_checksums'
PARAM_EXCLUDED_EXTENSIONS = \
    'module_checksum_upgrade.checksum_excluded_extensions'


class Module(models.Model):
    _inherit = 'ir.module.module'

    @api.multi
    def _get_checksum_dir(self):
        self.ensure_one()

        excluded_extensions = self.env["ir.config_parameter"].get_param(
            PARAM_EXCLUDED_EXTENSIONS,
            'pyc,pyo',
        ).split(",")

        module_path = get_module_path(self.name)
        if module_path and os.path.isdir(module_path):
            checksum_dir = dirhash(
                module_path,
                'sha1',
                excluded_extensions=excluded_extensions,
            )
        else:
            checksum_dir = False

        return checksum_dir

    @api.model
    def _get_saved_checksums(self):
        Icp = self.env['ir.config_parameter']
        return json.loads(Icp.get_param(PARAM_INSTALLED_CHECKSUMS, '{}'))

    @api.model
    def _save_checksums(self, checksums):
        Icp = self.env['ir.config_parameter']
        Icp.set_param(PARAM_INSTALLED_CHECKSUMS, json.dumps(checksums))

    @api.model
    def _save_installed_checksums(self):
        checksums = {}
        installed_modules = self.search([('state', '=', 'installed')])
        for module in installed_modules:
            checksums[module.name] = module._get_checksum_dir()
        self._save_checksums(checksums)

    @api.model
    def _get_modules_partially_installed(self):
        return self.search([
            '!',
            ('state', 'in', ('installed', 'uninstalled', 'uninstallable')),
        ])

    @api.model
    def _get_modules_with_changed_checksum(self):
        saved_checksums = self._get_saved_checksums()
        installed_modules = self.search([('state', '=', 'installed')])
        return installed_modules.filtered(
            lambda r: r._get_checksum_dir() != saved_checksums.get(r.name),
        )

    @api.model
    def upgrade_changed_checksum(self):
        """ Run an upgrade of the database, upgrading only changed modules.

        Installed modules for which the checksum has changed since the
        last successful run of this method are marked "to upgrade",
        then the normal Odoo scheduled upgrade process
        is launched.

        If there is no module with a changed checksum, and no module in state
        other than installed, uninstalled, uninstallable, this method does
        nothing, otherwise the normal Odoo upgrade process is launched.

        After a successful upgrade, the checksums of installed modules are
        saved.

        In case of error during the upgrade, an exception is raised.
        If any module remains to upgrade or to uninstall after the upgrade
        process, this method returns False. It returns True only in case
        of complete success.
        """
        _logger.info("Upgrade starting...")

        _logger.info("Updating modules list...")
        self.update_list()
        changed_modules = self._get_modules_with_changed_checksum()
        if not changed_modules and not self._get_modules_partially_installed():
            _logger.info("No checksum change detected in installed modules "
                         "and all modules installed, nothing to do.")
            return True
        _logger.info("Marking the following module to upgrade "
                     "following checksum change: %s...",
                     ','.join(changed_modules.mapped('name')))
        changed_modules.button_upgrade()
        self.env.cr.commit()  # pylint: disable=invalid-commit

        _logger.info("Upgrading...")
        self.env['base.module.upgrade'].upgrade_module()
        self.env.cr.commit()  # pylint: disable=invalid-commit

        _logger.info("Upgrade successful, updating checksums...")
        self._save_installed_checksums()
        self.env.cr.commit()  # pylint: disable=invalid-commit

        partial_modules = self._get_modules_partially_installed()
        if partial_modules:
            _logger.info("Upgrade successful "
                         "but incomplete for the following modules: %s",
                         ','.join(partial_modules.mapped('name')))
            return False
        else:
            _logger.info("Upgrade complete.")
            return True
