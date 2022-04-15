This module allows to **import/export files** from/to backend servers.

A backend server is defined by the basic `storage_backend <https://github.com/OCA/storage/tree/12.0/storage_backend>`_ OCA module, while it can be configured (amazon S3, sftp,...) with additional modules from the `storage <https://github.com/oca/storage>`_ repository.

The imported files (and the files to be exported) are stored in Odoo as ``attachment.queue`` objects, defined by the `attachment_queue <https://github.com/OCA/server-tools/tree/12.0/attachment_queue>`_ module while the importation itself (resp. exportation) is realized by **"Attachments Import Tasks"** (resp. "Attachments Export Tasks") defined by this current module.
