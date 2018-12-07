.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Attachment Sync Amazon S3
=========================

Automatically upload Account Related attachments to Amazon S3 Bucket

Installation
============
For this module to work you need:

* pip3 install boto3
* pip3 install botocore

Configuration
=============

Add the following Amazon S3 Credentials obtained from the console:

* *S3 Bucket Name*
* *S3 Access key ID*
* *S3 Secret Key*

For Security reasons, the S3 Credentials can be added to Odoo config file:

* s3_bucket_name = Bucketname
* s3_access_key_id = xxxx...
* s3_secret_access_key = xxxx...

Credits
=======

Contributors
------------

* Dan Kiplangat, Sunflower IT <dan@sunflowerweb.nl>
* Tom Blauwendraat, Sunflower IT <tom@sunflowerweb.nl>

Images
------

* Wikimedia Commons: `Icon <https://commons.wikimedia.org/wiki/File:AWS_Simple_Icons_AWS_Cloud.svg>`_.

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
