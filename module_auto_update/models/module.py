# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, fields, models
from odoo.modules.module import get_module_path

_logger = logging.getLogger(__name__)
try:
    from checksumdir import dirhash
except ImportError:
    _logger.debug('Cannot `import checksumdir`.')


class Module(models.Model):
    _inherit = 'ir.module.module'

    checksum_dir = fields.Char(
        compute='_compute_checksum_dir',
    )
    checksum_installed = fields.Char()

    @api.depends('name')
    def _compute_checksum_dir(self):
        exclude = self.env["ir.config_parameter"].get_param(
            "module_auto_update.checksum_excluded_extensions",
            "pyc,pyo",
        ).split(",")

        for r in self:
            try:
                r.checksum_dir = dirhash(
                    get_module_path(r.name),
                    'sha1',
                    excluded_extensions=exclude,
                )
            except TypeError:
                _logger.debug(
                    "Cannot compute dir hash for %s, module not found",
                    r.display_name)

    @api.multi
    def _store_checksum_installed(self, vals):
        """Store the right installed checksum, if addon is installed."""
        if 'checksum_installed' not in vals:
            try:
                version = vals["latest_version"]
            except KeyError:
                return  # Not [un]installing/updating any addon
            if version is False:
                # Uninstalling
                self.write({'checksum_installed': False})
            else:
                # Installing or updating
                for one in self:
                    one.checksum_installed = one.checksum_dir

    @api.model
    def create(self, vals):
        res = super(Module, self).create(vals)
        res._store_checksum_installed(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(Module, self).write(vals)
        self._store_checksum_installed(vals)
        return res
