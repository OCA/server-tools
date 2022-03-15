* Go to the menu configuration => Technical => Email => Message And Attachment Vacuum Rules
* Add the adequates rules for your company. On each rule, you can indicate the models, type and subtypes for which you want to delete the messages, along with a retention time (in days). Or for attachment, you can specify a substring of the name.
* Customize the maximum number of records can be deleted on each execution of the vacuum process, by modifying the last parameter in respective crons AutoVacuum Mails and Messages and AutoVacuum Attachments.
* Activate the cron AutoVacuum Mails and Messages and/or AutoVacuum Attachments

It is recommanded to run it frequently and when the system is not very loaded.
(For instance : once a day, during the night.)
