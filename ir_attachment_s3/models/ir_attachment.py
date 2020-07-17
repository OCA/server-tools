# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
from odoo import api, models, tools

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    _logger.debug('Cannot boto3')

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'    

    def unlink(self):
        # operations
        if self.type == 'url':
            if self.url != False:
                if 'amazonaws.com' in self.url:
                    self.remove_to_s3()
        # return
        return models.Model.unlink(self)    
    
    @api.one        
    def remove_to_s3(self):
        destination_filename = 'ir_attachments/%s/%s/%s' % (
            self.res_model,
            self.res_id,
            self.name.encode('ascii', 'ignore').decode('ascii')
        )
        # decode
        if isinstance(destination_filename, str):
            decoded = False
        else:
            destination_filename = unicode_or_str.decode(destination_filename)
            decoded = True
        # client
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=tools.config.get('aws_access_key_id'),
                aws_secret_access_key=tools.config.get('aws_secret_key_id'),
                region_name=tools.config.get('aws_region_name')
            )
            s3_client.delete_object(
                Bucket=self.env['ir.config_parameter'].sudo().get_param('ir_attachment_s3_bucket_name'),
                Key=destination_filename[1:-1]
            )
        except:
            _logger.debug('Boto3 error')

    def upload_to_s3(self):
        # define
        source_path = '/var/lib/odoo/.local/share/Odoo/filestore/%s/%s' % (
            tools.config.get('db_name'),
            self.store_fname
        )
        destination_filename = 'ir_attachments/%s/%s/%s' % (
            self.res_model,
            self.res_id,
            self.name.encode('ascii', 'ignore').decode('ascii')
        )
        # decode
        if isinstance(destination_filename, str):
            decoded = False
        else:
            destination_filename = unicode_or_str.decode(destination_filename)
            decoded = True
        # operations
        if not os.path.exists(source_path):
            self.unlink()
        else:
            # client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=tools.config.get('aws_access_key_id'),
                aws_secret_access_key=tools.config.get('aws_secret_key_id'),
                region_name=tools.config.get('aws_region_name')
            )                
            try:
                with open(source_path, "rb") as f:
                    s3_client.upload_fileobj(
                        f,
                        self.env['ir.config_parameter'].sudo().get_param('ir_attachment_s3_bucket_name'),
                        destination_filename,
                        ExtraArgs={'ACL':'public-read'}
                    )
                # update
                self.type = 'url'
                self.url = "https://s3-%s.amazonaws.com/%s/%s" % (
                    tools.config.get('aws_region_name'),
                    self.env['ir.config_parameter'].sudo().get_param('ir_attachment_s3_bucket_name'),
                    destination_filename
                )
            except ClientError as e:
                _logger.info(e)
                
    @api.model    
    def cron_action_s3_upload_ir_attachments(self):            
        ir_attachment_ids = self.env['ir.attachment'].search(
            [
                ('type', '=', 'binary'),
                ('res_model', '!=', False),
                ('res_id', '>', 0)
            ],
            limit=1000
        )                
        if len(ir_attachment_ids)>0:
            for ir_attachment_id in ir_attachment_ids:
                ir_attachment_id.upload_to_s3()                            