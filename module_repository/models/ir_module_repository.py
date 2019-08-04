# coding: utf-8
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from openerp import api, fields, models, modules
from openerp.tools import config

_logger = logging.getLogger(__name__)

try:
    import git
except ImportError:
    _logger.debug("Cannot import git librairy. Run 'pip install GitPython'")


class IrModuleRepository(models.Model):
    _name = 'ir.module.repository'
    _order = 'name'

    _VERSION_CONTROL_SELECTION = [
        ('git', 'Git'),
        ('unknown', 'Unknown'),
    ]

    _STATE_SELECTION = [
        ('used', 'Used'),
        'unused', 'Unused',
    ]

    # Column Section
    name = fields.Char(
        string='Name of the Repository', required=True, readonly=True)

    path = fields.Char(
        string='Complete path of the Repository', readonly=True)

    is_odoo_core = fields.Boolean(string='Is Odoo Core', readonly=True)

    module_ids = fields.One2many(
        comodel_name='ir.module.module', inverse_name='repository_id',
        string='Modules', readonly=True)

    module_qty = fields.Integer(
        compute='_compute_module_qty', string='Quantity of Modules',
        store=True)

    installed_module_qty = fields.Integer(
        compute='_compute_module_qty', string='Quantity of Installed Modules',
        store=True)

    state = fields.Char(
        selection=_STATE_SELECTION, compute='_compute_module_qty',
        string='State', store=True)

    version_control_type = fields.Selection(
        selection=_VERSION_CONTROL_SELECTION, string='Version Control Type',
        readonly=True, default='unknown',
        help="Type of Repository: Git, etc...")

    url = fields.Char(string='URL', readonly=True)

    branch = fields.Char(string='Branch', readonly=True)

    local_modification_qty = fields.Integer(
        string='Quantity of Local Modifications', readonly=True)

    # Compute Section
    @api.multi
    @api.depends('module_ids.state')
    def _compute_module_qty(self):
        for repository in self:
            repository.module_qty = len(repository.module_ids)
            repository.installed_module_qty = len(
                repository.module_ids.filtered(
                    lambda x: x.state in [
                        'to upgrade', 'to install', 'installed']))
            if repository.installed_module_qty == 0:
                repository.state = 'unused'
            else:
                repository.state = 'used'

    @api.model
    def _create_repositories_from_addons_path(self):
        _logger.info("Update Repositories List from addons_path ...")
        for addons_path in [
                x.strip() for x in config['addons_path'].split(',')]:
            web_path = os.path.join(addons_path, 'web')
            base_path = os.path.join(addons_path, 'base')
            path = os.path.dirname(addons_path + '/')
            is_odoo_core = False
            if modules.get_module_path('web') == web_path:
                # We remove 'addons'
                path = path.replace('/addons', '')
                is_odoo_core = True
            elif modules.get_module_path('base') == base_path:
                # We remove 'openerp/addons'
                path = path.replace('/openerp/addons', '')
                is_odoo_core = True

            if not self.search([('path', '=', path)]):
                if is_odoo_core:
                    name = 'Odoo'
                else:
                    name = [x for x in path.split('/') if x][-1]
                self.create({
                    'name': name,
                    'path': path,
                    'is_odoo_core': is_odoo_core,
                })

    @api.multi
    def update_information(self):
        _logger.info(
            "Update Repositories Informations running git command ...")

        path_list = []
        for repository in self:
            path_list.append(repository.path)
            repository.write(repository._prepare_from_source_control())

    # Private section
    @api.multi
    def _prepare_from_source_control(self):
        self.ensure_one()
        try:
            repo = git.Repo(self.path)
        except Exception:
            repo = False
        if repo:
            url = [x for x in repo.remotes[0].urls][0]
            try:
                branch = repo.active_branch.name
            except TypeError:
                # Handle case where the HEAD is detached.
                # https://github.com/gitpython-developers/GitPython/issues/633
                branch = ''
            diff = repo.git.status(short=True)
            qty = diff and len(diff.split('\n')) or 0
            return {
                'url': url, 'branch': branch,
                'version_control_type': 'git', 'local_modification_qty': qty}
        return {
            'url': '', 'branch': '',
            'version_control_type': 'unknown', 'local_modification_qty': 0}
