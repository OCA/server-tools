# -*- encoding: utf-8 -*-
##############################################################################
#
#    Tools - Repository of Modules for Odoo
#    Copyright (C) 2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from subprocess import Popen, PIPE

import git
from bzrlib import branch as bzr_branch

from openerp import modules
from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv.orm import Model


class ir_module_repository(Model):
    _description = "Modules Repository"
    _name = 'ir.module.repository'
    _order = 'name'

    _TYPE_SELECTION = [
        ('unknown', 'Unknown'),
        ('git', 'Git'),
        ('bazaar', 'Bazaar'),
    ]

    # Getter Section
    def _get_qty(self, cr, uid, ids, name, arg, context=None):
        """Return the price by the volume"""
        res = {}
        imm_obj = self.pool['ir.module.module']
        for imp in self.browse(cr, uid, ids, context=context):
            imm_ids = imm_obj.search(cr, uid, [
                ('id', 'in', [x.id for x in imp.module_ids]),
                ('state', 'in', ['installed'])])
            res[imp.id] = {
                'module_qty': len(imp.module_ids),
                'installed_module_qty': len(imm_ids),
            }
        return res

    def _get_state(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for imp in self.browse(cr, uid, ids, context=context):
            if imp.installed_module_qty == 0:
                res[imp.id] = 'unused'
            else:
                res[imp.id] = 'used'
        return res

    # Column Section
    _columns = {
        'name': fields.char(
            'Name of the Repository', required=True, readonly=True),
        'path': fields.char(
            'Complete path of the Repository', readonly=True),
        'module_ids': fields.one2many(
            'ir.module.module', 'repository_id', 'Modules', readonly=True),
        'installed_module_qty': fields.function(
            _get_qty, type='integer', multi='_get_qty',
            string='Quantity of Installed Modules'),
        'module_qty': fields.function(
            _get_qty, type='integer', multi='_get_qty',
            string='Quantity of Modules'),
        'type': fields.selection(
            _TYPE_SELECTION, 'Type of Repository', readonly=True,
            help="Type of Repository: Git, Bazaar, etc..."),
        'url': fields.char(
            'URL', readonly=True),
        'branch': fields.char(
            'Branch', readonly=True),
        'revision': fields.char(
            'Revision', readonly=True),
        'local_modification_qty': fields.integer(
            'Quantity of Local Modifications', readonly=True),
        'state': fields.function(_get_state, string="State", type='char'),
    }

    _defaults = {
        'type': 'unknown',
    }

    # Public section
    def init(self, cr):
        self.update_information(cr, SUPERUSER_ID)

    def update_information(self, cr, uid, context=None):
        imm_obj = self.pool['ir.module.module']
        # Get existing repository
        imr_list = self.browse(
            cr, uid, self.search(
                cr, uid, [], context=context), context=context)
        imr_curr = {}
        for imr in imr_list:
            imr_curr[imr.path] = imr.id

        # Update list of repositories
        for module in imm_obj.browse(
                cr, uid, imm_obj.search(
                    cr, uid, [], context=context), context=context):
            module_path = modules.get_module_path(module.name)
            if module_path:
                path = module_path.rstrip(module.name)
                id = imr_curr.get(path, False)
                if not id:
                    # Create new repository
                    id = self.create(cr, uid, {
                        'name': 'TEMPORARY NAME',
                        'path': path,
                        }, context=context)
                    imr_curr[path] = id
                imm_obj.write(
                    cr, uid, [module.id], {'repository_id': id},
                    context=context)

        # Update information of All repositories
        ids = self.search(cr, uid, [], context=context)
        path_list = []
        for imr in self.browse(cr, uid, ids, context=context):
            if imr.module_qty == 0:
                # Delete Obsolete repository, that is not linked to any modules
                self.unlink(cr, uid, [imr.id], context=context)
            else:
                path_list.append(imr.path)
                vals = self._read_git_information(
                    cr, uid, imr, context=context)
                if not vals:
                    vals = self._read_bazaar_information(
                        cr, uid, imr, context=context)
                if not vals:
                    vals = {
                        'url': '', 'branch': '', 'revision': '',
                        'type': 'unknown', 'local_modification_qty': 0}
                self.write(cr, uid, [imr.id], vals, context=context)

        # Compute Friendly name
        if len(path_list) > 0:
            common_path = ''
            for i in range(0, len(path_list[0])):
                common = True
                for item in path_list:
                    common = common and (item[0:i] == path_list[0][0:i])
                if common:
                    common_path = path_list[0][0:i]
                else:
                    break

            ids = self.search(cr, uid, [], context=context)
            for imr in self.browse(cr, uid, ids, context=context):
                vals = {
                    'name': imr.path[len(common_path):].strip('/')
                }
                self.write(cr, uid, [imr.id], vals, context=context)

    # Private section
    def _parse(self, my_string, begin_string, end_string, strip=False):
        if strip:
            my_string = my_string.strip(strip)
        begin = my_string.find(begin_string)
        if begin != -1:
            my_string = my_string[begin + len(begin_string):]
            if strip:
                my_string = my_string.strip(strip)
            end = my_string.find(end_string)
            if end != -1:
                return my_string[:end]
        return ''

    def _read_bazaar_information(self, cr, uid, repository, context=None):
        try:
            diff = False
            repo = bzr_branch.Branch.open(repository.path)
            proc = Popen([
                'bzr', 'status', '--short', repository.path], shell=False,
                stdout=PIPE)
            diff = proc.communicate()[0]
        except:
            repo = False
        if repo:
            url = repo.get_parent().replace('bzr+ssh', 'https')
            revision = repo.revno()
            if diff:
                qty = len(diff.strip('\n').split('\n'))
            else:
                qty = 0

            return {
                'url': url, 'branch': '', 'revision': revision,
                'type': 'bazaar', 'local_modification_qty': qty}
        return False

    def _read_git_information(self, cr, uid, repository, context=None):
        try:
            repo = git.Repo(repository.path)
        except:
            repo = False
        if repo and repo.path != '/.git':
            url = self._parse(
                repo.git.remote(verbose=True), 'origin\t', ' (fetch)')
            branch = self._parse(
                repo.git.branch(verbose=True), '* ', ' ')
            revision = self._parse(
                repo.git.branch(verbose=True),
                '* %s ' % (branch), ' ', ' ')
            diff = repo.git.status(short=True)
            if diff != '':
                qty = len(diff.split('\n'))
            else:
                qty = 0
            return {
                'url': url, 'branch': branch, 'revision': revision,
                'type': 'git', 'local_modification_qty': qty}
        return False
