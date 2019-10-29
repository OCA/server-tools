import pytz
import logging

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.service import db


_logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    _logger.warning('pip3 install --upgrade boto3')


_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'years': lambda interval: relativedelta(years=interval)
}
INTERVAL_NUMBER = 1


class S3Backup(models.Model):
    _name = 's3.backup'
    _description = 'Database Backup to AWS S3'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    periodicity = fields.Selection([
        ('days', 'Daily'),
        ('weeks', 'Weekly'),
        ('months', 'Monthly'),
        ('years', 'Yearly')
    ], string='Periodicity', required=True)
    bucket_name = fields.Char(string='Bucket name', required=True)
    folder = fields.Char(string='Folder')
    days_to_keep = fields.Integer(string='Days to Keep', required=True)
    nextcall = fields.Date(string='Next Execution Date',
                           default=fields.Date.context_today, required=True)

    @api.model
    def _get_api_keys(self):
        aws_access_key_id = self.env['ir.config_parameter'].sudo(
        ).get_param('backup_s3.aws_access_key_id')
        aws_secret_access_key = self.env['ir.config_parameter'].sudo(
        ).get_param('backup_s3.aws_secret_access_key')
        return aws_access_key_id, aws_secret_access_key

    @api.model
    def _get_client(self):
        aws_access_key_id, aws_secret_access_key = self._get_api_keys()
        client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        return client

    @api.multi
    def action_backup(self):
        db_name = self.env.cr.dbname
        successful = self.browse()
        for rec in self.filtered(lambda r: r.active and r.nextcall == date.today()):
            fname = "{:%Y_%m_%d_%H_%M_%S}-{}-backup.zip".format(
                datetime.now(), db_name)
            backup_file = db.dump_db(db_name, None)
            try:
                client = rec._get_client()
                client.upload_fileobj(
                    backup_file, rec.bucket_name, '%s/%s' % (rec.folder, fname))
            except ClientError as e:
                logging.error(e)
            finally:
                rec.nextcall += _intervalTypes[rec.periodicity](
                    INTERVAL_NUMBER)
                backup_file.close()
            successful |= rec
        successful.cleanup()

    @api.multi
    def cleanup(self):
        utc = pytz.UTC
        for rec in self.filtered("days_to_keep"):
            client = rec._get_client()
            oldest = datetime.now() - timedelta(days=rec.days_to_keep)
            response = client.list_objects_v2(Bucket=rec.bucket_name)
            keys_to_delete = [{
                'Key': object['Key']
            } for object in response['Contents']
                if object['LastModified'].replace(tzinfo=utc) < utc.localize(oldest)
                and rec.folder in object['Key']]
            if keys_to_delete:
                client.delete_objects(Bucket=rec.bucket_name, Delete={
                                      'Objects': keys_to_delete})

    @api.model
    def action_backup_all(self):
        """Run all scheduled backups."""
        return self.search([]).action_backup()
