# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from threading import current_thread


class Base(models.AbstractModel):
    _inherit = 'base'

    @property
    def remote(self):
        try:
            remote_addr = current_thread().environ["REMOTE_ADDR"]
        except (KeyError, AttributeError):
            return self.env['res.remote']
        return self.env['res.remote']._get_remote(remote_addr)
