# -*- coding: utf-8 -*-
# Copyright 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from ..tasks.google_drive import GoogleDriveTask


class Location(models.Model):
    _inherit = 'external.file.location'
    _description = 'Location Google Drive'

    @api.model
    def _get_classes(self):
        """Extend this method to add Google Drive option"""
        res = super(Location, self)._get_classes()
        res['google_drive'] = ('Google Drive', GoogleDriveTask)
        return res

    def _get_access_token(self):
        return self.env['google.drive.config'].get_access_token()
