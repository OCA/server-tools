# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class IrModuleAuthor(models.Model):
    _name = 'ir.module.author'
    _description = 'Modules Authors'

    name = fields.Char(string='Name', required=True)

    installed_module_ids = fields.Many2many(
        string='Modules', comodel_name='ir.module.module',
        relation='ir_module_module_author_rel')

    installed_module_qty = fields.Integer(
        string="Installed Modules Quantity",
        compute='_compute_installed_module_qty', store=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'The name of the modules author should be unique per database!'),
    ]

    @api.multi
    @api.depends('installed_module_ids')
    def _compute_installed_module_qty(self):
        for author in self:
            author.installed_module_qty = len(author.installed_module_ids)

    @api.model
    def _get_or_create(self, name):
        authors = self.search([('name', '=', name)])
        if authors:
            return authors[0]
        else:
            return self.create({'name': name})
