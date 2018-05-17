# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
import logging
import os

from openerp import api, exceptions, models, tools
from openerp.modules.module import get_module_path

from ..addon_hash import addon_hash

PARAM_INSTALLED_CHECKSUMS = \
    'module_auto_update.installed_checksums'
PARAM_EXCLUDE_PATTERNS = \
    'module_auto_update.exclude_patterns'
DEFAULT_EXCLUDE_PATTERNS = \
    '*.pyc,*.pyo,i18n/*.pot,i18n_extra/*.pot,static/*'

_logger = logging.getLogger(__name__)


class FailedUpgradeError(exceptions.Warning):
    pass


class IncompleteUpgradeError(exceptions.Warning):
    pass


def ensure_module_state(env, modules, state):
    # read module states, bypassing any Odoo cache
    env.cr.execute(
        "SELECT name FROM ir_module_module "
        "WHERE id IN %s AND state != %s",
        (tuple(modules.ids), state),
    )
    names = [r[0] for r in env.cr.fetchall()]
    if names:
        raise FailedUpgradeError(
            "The following modules should be in state '%s' "
            "at this stage: %s. Bailing out for safety." %
            (state, ','.join(names), ),
        )


class Module(models.Model):
    _inherit = 'ir.module.module'

    @api.multi
    def _get_checksum_dir(self):
        self.ensure_one()

        exclude_patterns = self.env["ir.config_parameter"].get_param(
            PARAM_EXCLUDE_PATTERNS,
            DEFAULT_EXCLUDE_PATTERNS,
        )
        exclude_patterns = [p.strip() for p in exclude_patterns.split(',')]
        keep_langs = self.env['res.lang'].search([]).mapped('code')

        module_path = get_module_path(self.name)
        if module_path and os.path.isdir(module_path):
            checksum_dir = addon_hash(
                module_path,
                exclude_patterns,
                keep_langs,
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
            ('state', 'in', ('to install', 'to remove', 'to upgrade')),
        ])

    @api.model
    def _get_modules_with_changed_checksum(self):
        saved_checksums = self._get_saved_checksums()
        installed_modules = self.search([('state', '=', 'installed')])
        return installed_modules.filtered(
            lambda r: r._get_checksum_dir() != saved_checksums.get(r.name),
        )

    @api.model
    def upgrade_changed_checksum(self, overwrite_existing_translations=False):
        """Run an upgrade of the database, upgrading only changed modules.

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
        process, an exception is raised as well.

        Note: this method commits the current transaction at each important
        step, it is therefore not intended to be run as part of a
        larger transaction.
        """
        _logger.info(
            "Checksum upgrade starting (i18n-overwrite=%s)...",
            overwrite_existing_translations
        )

        tools.config['overwrite_existing_translations'] = \
            overwrite_existing_translations

        _logger.info("Updating modules list...")
        self.update_list()
        changed_modules = self._get_modules_with_changed_checksum()
        if not changed_modules and not self._get_modules_partially_installed():
            _logger.info("No checksum change detected in installed modules "
                         "and all modules installed, nothing to do.")
            return
        _logger.info("Marking the following modules to upgrade, "
                     "for their checksums changed: %s...",
                     ','.join(changed_modules.mapped('name')))
        changed_modules.button_upgrade()
        self.env.cr.commit()  # pylint: disable=invalid-commit
        # in rare situations, button_upgrade may fail without
        # exception, this would lead to corruption because
        # no upgrade would be performed and save_installed_checksums
        # would update cheksums for modules that have not been upgraded
        ensure_module_state(self.env, changed_modules, 'to upgrade')

        _logger.info("Upgrading...")
        self.env['base.module.upgrade'].upgrade_module()
        self.env.cr.commit()  # pylint: disable=invalid-commit

        _logger.info("Upgrade successful, updating checksums...")
        self._save_installed_checksums()
        self.env.cr.commit()  # pylint: disable=invalid-commit

        partial_modules = self._get_modules_partially_installed()
        if partial_modules:
            raise IncompleteUpgradeError(
                "Checksum upgrade successful "
                "but incomplete for the following modules: %s" %
                ','.join(partial_modules.mapped('name'))
            )

        _logger.info("Checksum upgrade complete.")
