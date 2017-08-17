# -*- coding: utf-8 -*-
import pip
from botocore.exceptions import ClientError

from odoo.tests import common
from odoo import exceptions

try:
    from moto import mock_s3
except ImportError:
    pip.main(['install', 'moto'])

model = 'odoo.addons.auto_backup.models.db_backup'


class TestConnectionException(ClientError):
    def __init__(self):
        super(TestConnectionException, self).__init__('test', 'test')


class S3TestDbBackup(common.TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(S3TestDbBackup, self).setUp()
        self.Model = self.env["db.backup"]
        self.s3_bucket_name = 'sample_bucket_name'
        self.s3_auth_key = 'auth_key'
        self.s3_auth_secret = 'auth_secret'
        self.s3_region = 'eu-west-1'

    def new_record(self, method='s3'):
        vals = {
            'name': u'Têst backup',
            'method': method,
        }

        if method == 's3':
            vals.update({
                's3_bucket_name': self.s3_bucket_name,
                's3_auth_key': self.s3_auth_key,
                's3_auth_secret': self.s3_auth_secret,
                's3_region': self.s3_region,
            })
        self.vals = vals
        return self.Model.create(vals)

    def test_compute_name_s3(self):
        """ It should create proper Bucket Name """
        rec_id = self.new_record()
        self.assertEqual(
            '%(s3_bucket_name)s' % {'s3_bucket_name': self.vals['s3_bucket_name']},
            rec_id.name,
        )

    @mock_s3
    def test_s3_connection(self):
        """ It should assert s3 uri """
        rec_id = self.new_record()
        s3 = rec_id.s3_connection()
        self.assertEqual(s3._endpoint.host, 'https://s3-%s.amazonaws.com' % self.s3_region)

    @mock_s3
    def test_action_s3_test_connection_success(self):
        """ It should raise connection succeeded warning """
        rec_id = self.new_record()
        with self.assertRaises(exceptions.Warning) as e:
            rec_id.action_s3_test_connection()
        self.assertEqual(
            "Connection Test Succeeded!",
            str(e.exception[0])
        )

    @mock_s3
    def test_action_backup_s3(self):
        """ It should backup local database """
        rec_id = self.new_record()
        rec_id.action_backup()

        s3 = rec_id.s3_connection()
        objects = s3.list_objects(Bucket=rec_id.s3_bucket_name)['Contents']
        self.assertGreaterEqual(len(objects), 1)
