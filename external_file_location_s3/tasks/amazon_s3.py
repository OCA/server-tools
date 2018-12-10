# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import boto3
import botocore
from odoo.tools import config
from odoo import exceptions


class AmazonS3Task:
    _key = 'amazon_s3'
    _name = 'AMAZON S3'
    _synchronize_type = None
    _default_port = False
    _hide_login = True
    _hide_password = True
    _hide_port = True
    _hide_address = True

    def __init__(self, bucket_name, access_key_id, secret_access_key):
        self.conn = boto3.client(
            's3', aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key)
        self.bucket_name = bucket_name

    def setcontents(self, path, data=None):
        """Upload to S3 Via put_object()"""
        client = self.conn
        try:
            client.put_object(Bucket=self.bucket_name, Body=data, Key=path)
        except botocore.exceptions.ClientError as client_err:
            raise exceptions.ValidationError(
                "AWS S3: " + client_err.response['Error']['Message'])

    @staticmethod
    def connect(location):
        if config.get('s3_bucket_name') and config.get('s3_access_key_id'):
            bucket_name = config.get('s3_bucket_name')
            access_key_id = config.get('s3_access_key_id')
            secret_access_key = config.get('s3_secret_access_key')
            conn = AmazonS3Task(bucket_name, access_key_id, secret_access_key)
        else:
            conn = AmazonS3Task(
                location.bucket_name,
                location.s3_access_key_id,
                location.secret_access_key)
        return conn
