# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from ..tasks.amazon_s3 import AmazonS3Task


class Location(models.Model):
    _inherit = 'external.file.location'
    _description = 'Location Amazon S3 Bucket'

    s3_access_key_id = fields.Char('Access Key ID')
    secret_access_key = fields.Char('Secret Key')
    bucket_name = fields.Char('Bucket Name')

    @api.model
    def _get_classes(self):
        """Extend this method to add Amazon S3 option"""
        res = super(Location, self)._get_classes()
        res['amazon_s3'] = ('Amazon S3', AmazonS3Task)
        return res

