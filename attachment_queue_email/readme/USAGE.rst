Adding an **"Attachment Condition"** to your *Incoming Mail Server* configuration will lead to the creation of ``attachment.queue`` objects from emails attachments coming from this server and matching the given *Attachment Condition*.

  🔎 Recalling that, as the *Incoming Mail Servers* has only one *"Create a New Record"* field, the emails coming from that server **cannot be used to create other type of objects** than ``attachment.queue``.

Filling the condition's **File Type** field will spread this value to the newly created ``attchment.queue`` objects so they can be processed by a custom module following this **File Type** field value.
