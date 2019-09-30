This module extends ir.attachment model with some new fields for a better control for import and export of files.

The main feature is the possibility to create a queue of attachment and have a cron process it.
The attachments will be processed depending on their type.

An example of the use of this module, can be found in the module `attachment_synchronize`.
