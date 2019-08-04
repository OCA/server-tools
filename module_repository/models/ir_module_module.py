# coding: utf-8
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import api, fields, models, modules

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    repository_id = fields.Many2one(
        comodel_name='ir.module.repository', string='Repository',
        readonly=True)

    @api.model
    def update_list(self):
        ModuleRepository = self.env['ir.module.repository']
        res = super(IrModuleModule, self).update_list()
        ModuleRepository._create_repositories_from_addons_path()
        self._update_repository()
        repositories = ModuleRepository.search([])
        repositories.update_information()

        return res

    @api.model
    def _update_repository(self):
        _logger.info("Update Repositories of modules ...")
        ModuleRepository = self.env['ir.module.repository']
        moduleList = self.search([])

        for module in moduleList:
            repository_id = False
            module_path = modules.get_module_path(module.name)
            if module_path:
                repository_path = module_path[:- (len(module.name) + 1)]
                if repository_path.endswith('/openerp/addons'):
                    repository_path = repository_path.replace(
                        '/openerp/addons', '')
                if repository_path.endswith('/addons'):
                    repository_path = repository_path.replace('/addons', '')

                repository = ModuleRepository.search(
                    [('path', '=', repository_path)])
                if repository:
                    repository_id = repository.id
            module.write({'repository_id': repository_id})
