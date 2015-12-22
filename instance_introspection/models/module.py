# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: nhomar@vauxoo.com
# planned by: nhomar@vauxoo.com

import subprocess
import os

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _

class Module(models.Model):
    _inherit = 'ir.module.module'

    def get_sha(self, _path):
        try:
            label = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                            cwd=_path)
        except Exception:
            label = 'Not a valid git repository'
        return label
