.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================
Structured External Storage All Attachments
===========================================

On top of `external_file_location`, this module allows you to define a structured set of syncing rules (eg. a syncing scheme) for ir.attachment records to an external storage service supported by any installed `external_file_location_*` modules.

Mix-and-match is possible, as well as domain filtering - so for example it is possible to have the Sale Orders sync to Dropbox, 2018 Sale Orders to Google Drive also, and any invoices to S3.

The destination folder location and file name for the attachments can be configured based on the attachment object fields, so for example the Sale Order Name or the Sale Order Year (Python-calculated formula from date). A dressed-down Mako template language can be used for this.

Installation
============

- Install this module
- Install any `external_file_location_*` modules for external storage services that you want to use

Configuration
=============

- Configure the `external_file_location_*` modules with the correct username
  and password, and establish a connection (see README of those modules).
- Create the Sync Rules in *Settings->External Backup->Attachment Sync Rules*

  - Select the Odoo 'Model' of which you want the attachments to sync
  - Select which 'Sync' to use. These are based on protocols installed through
    the `external_file_location_*` modules (Google Drive, Dropbox, Amazon S3)
    and can be set per company
  - Sefine which files to include by 'Domain' and specify how they should be
    named through 'File Name Format', e.g "${object.name}" for Sale Orders 
    will save the file as SO001.pdf depending on the SO name
  - Save and either 'Sync Now' or 'Queue for Sync'

  .. image:: static/description/sync_rules.png
     :width: 700 px

- Queue for Sync button creates the metadata from old attachment files for the
  cron task: Settings > Technical > Database Structure > Meta Data Attachments
- Add more models you want to sync attachments for in "Referenceable Models"
  *Settings->Technical-> Database Structure -> Referenceable Models*
- Repeat this process for all desired sync rules. The sequence determines the
  order of evaluation of the rules.

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

