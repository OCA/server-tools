# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openerp import api, fields, models
from openerp.modules.module import get_module_path

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

    def _store_checksum_installed(self, vals):
        if self.env.context.get('retain_checksum_installed'):
            return
        if 'checksum_installed' not in vals:
            if vals.get('state') == 'installed':
                for r in self:
                    r.checksum_installed = r.checksum_dir
            elif vals.get('state') == 'uninstalled':
                self.write({'checksum_installed': False})

    @api.multi
    def button_uninstall_cancel(self):
        # TODO Use super() like in v10 after pull is merged
        # HACK https://github.com/odoo/odoo/pull/18597
        return self.with_context(retain_checksum_installed=True).write({
            'state': 'installed',
        })

    @api.multi
    def button_upgrade_cancel(self):
        # TODO Use super() like in v10 after pull is merged
        # HACK https://github.com/odoo/odoo/pull/18597
        return self.with_context(retain_checksum_installed=True).write({
            'state': 'installed',
        })

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
