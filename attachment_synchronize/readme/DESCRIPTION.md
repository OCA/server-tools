This module allows to **import/export files** from/to backend servers.

A backend server is defined by the basic
[fs_storage](https://github.com/OCA/storage/tree/16.0/fs_storage) OCA
module, while it can be configured (amazon S3, sftp,...) with additional
modules fs python libraries

The imported files (and the files to be exported) are stored in Odoo as
`attachment.queue` objects, defined by the
[attachment_queue](https://github.com/OCA/server-tools/tree/16.0/attachment_queue)
module while the importation itself (resp. exportation) is realized by
**"Attachments Import Tasks"** (resp. "Attachments Export Tasks")
defined by this current module.
