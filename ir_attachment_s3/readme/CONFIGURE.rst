The following configuration is required:

You will need to define the following parameters in the odoo.conf file

``
aws_access_key_id = xxxx
aws_secret_key_id = xxxxx
aws_region_name = eu-west-1
``

In addition, it will be necessary to go to Configuration> Technician> Configuration parameters to define the values of the following keys:

``
ir_attachment_s3_bucket_name
``

There we will define the name of the S3 bucket that will be used to upload the attachments

It is very important that the S3 bucket has public permission (or nobody will be able to access the files)