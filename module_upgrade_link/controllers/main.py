# -*- coding: utf-8 -*-
# Copyright 2017 Callino - https://www.callino.at/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
import logging


_logger = logging.getLogger(__name__)


class UpgradeController(http.Controller):

    @http.route(['/upgrade/<module>'], type='http', auth='user', method=['GET'])
    def upgrade(self, module, **kwargs):
        _logger.info("Request to upgrade %s", module)
        umodule = http.request.env["ir.module.module"].search([('state', '=', 'installed'), ('name', '=', module)])
        if not umodule:
            return "Module %s not found for upgrade" % module
        umodule.button_immediate_upgrade()
        return "OK"
