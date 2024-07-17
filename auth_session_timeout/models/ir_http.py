# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):

    _inherit = 'ir.http'

    @classmethod
    def _authenticate(cls, auth_method='user'):
        res = super(IrHttp, cls)._authenticate(auth_method=auth_method)
        if request and request.env and request.env.user:
            request.env.user._auth_timeout_check()
        return res
