Abstract module for importing emails attachments.

Each email's attachment matching a given **"Attachment Condition"** will be imported creating a new ``attachment.queue`` object. These ``attachment.queue`` objects are files wrapped with additional fields (mainly a **Filed Type** and a **State**) making them ready to be processed by a custom module as you can read in the `attachment_queue <https://github.com/OCA/server-tools/tree/12.0/attachment_queue>`_ documentation.
