Receive incoming emails from an S3-compatible bucket instead of IMAP/POP.

This module adds an "S3 Bucket" server type to Odoo's incoming mail servers.
It polls an S3 bucket for raw email files (`.eml`) and processes them through
Odoo's standard mail gateway (`mail.thread.message_process`).

**Typical use case**: AWS SES inbound email rules store messages in S3. This
module picks them up on a cron schedule, processes them into Odoo records
(leads, tickets, DMS documents, etc.), then archives or deletes the S3 objects.

Works with any S3-compatible storage (AWS S3, MinIO, Hetzner Object Storage,
DigitalOcean Spaces, etc.).
