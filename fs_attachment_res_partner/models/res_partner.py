# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, SUPERUSER_ID, exceptions, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('name', 'customer', 'supplier', 'company_id')
    def _compute_fs_rel_path(self):
        for partner in self:
            if partner.customer and partner.supplier:
                filesystem_storage_rel_path = _("Customers & Vendors/%s") % partner.display_name
            elif partner.customer:
                filesystem_storage_rel_path = _("Customers/%s") % partner.display_name
            elif partner.supplier:
                filesystem_storage_rel_path = _("Vendors/%s") % partner.display_name
            else:
                filesystem_storage_rel_path = _("Contact/%s") % partner.display_name
            partner.filesystem_storage_rel_path = filesystem_storage_rel_path

    @api.multi
    @api.depends('filesystem_storage_rel_path', 'company_id')
    def _compute_fs_uri(self):
        for partner in self:
            partner.filesystem_uri = "%s/%s" % (partner.company_id.uri_storage_path, partner.filesystem_storage_rel_path)

    def _set_fs_rel_path(self):
        pass

    filesystem_storage_rel_path = fields.Char('Filesystem Rel Path', compute='_compute_fs_rel_path',
                                              inverse='_set_fs_rel_path', store=True, index=True)
    filesystem_uri = fields.Char('Directory URI', compute='_compute_fs_uri', store=True)
