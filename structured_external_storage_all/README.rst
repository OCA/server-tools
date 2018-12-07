.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================
Structured External Storage All Attachments
===========================================

Creates ir.attachment.metadata records for the attachments to sync to respective
clouds: Dropbox, Google Drive, Amazon S3 Bucket.

Installation
============
- Just install

Configuration
=============

- Create the Sync Rules in *Settings->External Backup->Attachment Sync Rules*

  - Select the Odoo 'Model' of which you want the attachments to sync
  - Select which 'Sync' to use. These are based on protocols installed through
    the attachment_sync_xxx (Google Drive, Dropbox, Amazon S3) modules and can
    be set per company
  - Sefine which files to include by 'Domain' and specify how they should be
    named through 'File Name Format'
  - Save and either 'Sync Now' or 'Queue for Sync'

  .. image:: structured_external_storage_all/static/description/sync_rules.png
     :width: 700 px

- Queue for Sync button creates the metadata from old attachment files for the
  cron task: Settings > Technical > Database Structure > Meta Data Attachments
- Add more models you want to sync attachments for in "Referenceable Models"
  *Settings->Technical-> Database Structure -> Referenceable Models*
- Use Jinja templates for custom file names E.g "${object.name}" for Sale Orders 
  will save the file as SO001.pdf depending on the SO name

Credits
=======

Contributors
------------

* Dan Kiplangat, Sunflower IT <dan@sunflowerweb.nl>
* Tom Blauwendraat, Sunflower IT <tom@sunflowerweb.nl>

Images
------

* Kisspng: `Icon <https://www.kisspng.com/png-directory-structure-computer-icons-mbox-file-syste-616078/>`_.

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


