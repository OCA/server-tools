# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

PARAM_DEPRECATED = "module_auto_update.enable_deprecated"


class Module(models.Model):
    _inherit = 'ir.module.module'

    checksum_dir = fields.Char(
        deprecated=True,
        compute='_compute_checksum_dir',
    )
    checksum_installed = fields.Char(
        deprecated=True,
        compute='_compute_checksum_installed',
        inverse='_inverse_checksum_installed',
        store=False,
    )

    @api.depends('name')
    def _compute_checksum_dir(self):
        for rec in self:
            rec.checksum_dir = rec._get_checksum_dir()

    def _compute_checksum_installed(self):
        saved_checksums = self._get_saved_checksums()
        for rec in self:
            rec.checksum_installed = saved_checksums.get(rec.name, False)

    def _inverse_checksum_installed(self):
        checksums = self._get_saved_checksums()
        for rec in self:
            checksums[rec.name] = rec.checksum_installed
        self._save_checksums(checksums)

    @api.multi
    def _store_checksum_installed(self, vals):
        """Store the right installed checksum, if addon is installed."""
        if not self.env["base.module.upgrade"]._autoupdate_deprecated():
            # Skip if deprecated features are disabled
            return
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
