The operation of the addon is as follows:
- Every time an attachment is created (ir_attachment) that is stored on the server it is a file that will be "uploaded" to AWS S3
- Every time an attachment (ir_attachment) that has the URL type and is uploaded to AWS S3 is removed it is removed from there

In order not to delay the process of creating the files, there is a cron (ir_cron) defined with the name: S3 Upload Ir Attachments that with the frequency of 1 time a day (or with which we want to define) looks for attachments * that are NOT URL and uploads them to the S3 repository

* A limit of 1000 records is sought so that the process does not take hours if there are too many records