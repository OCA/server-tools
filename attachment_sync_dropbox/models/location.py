# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from ..tasks.dropbox import DropboxTask


class Location(models.Model):
    _inherit = 'external.file.location'
    _description = 'Location Dropbox'

    access_key_id = fields.Char()

    @api.model
    def _get_classes(self):
        """Extend this method to add dropbox option"""
        res = super(Location, self)._get_classes()
        res['dropbox'] = ('Dropbox', DropboxTask)
        return res
