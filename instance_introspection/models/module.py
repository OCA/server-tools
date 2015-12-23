# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: nhomar@vauxoo.com
# planned by: nhomar@vauxoo.com

import subprocess

from openerp import models
from openerp.tools.translate import _


class Module(models.Model):
    _inherit = 'ir.module.module'

    def clean_git_status(self, msg):
        '''Convert git status message in a printable dictionary.
        '''
        res = {
            'up_to_date': False,
            }
        if msg.find('up-to-date') > 0:
            res['up_to_date'] = True
        branch = msg.split('\n')[0]
        files = msg.split('\n\n')
        res.update({
            'branch': branch,
            'files': files,
            'full_status': msg
        })
        return res

    def get_info(self, _path):
        label = {}
        try:
            label['sha'] = subprocess.check_output([
                "git", "describe", "--always", "--dirty"], cwd=_path)
            label['status'] = self.clean_git_status(subprocess.check_output([
                "git", "status"], cwd=_path))
            label['remotes'] = subprocess.check_output([
                "git", "remote", "-v"], cwd=_path).split('\n')
        except Exception:
            label['sha'] = _('SHA: Not a valid git repository')
            label['status'] = {'message': _('STATUS: No valid information')}
            label['remotes'] = _('REMOTES: No valid information')
        return label

    def get_header(self, get_info):
        total_repositories = len(get_info)
        return {
            'total_repositories': total_repositories,
        }

