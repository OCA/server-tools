In your fetchmail configuration, you'll find a new list field `Folders to 
monitor`. Add your folders here in IMAP notation (usually something like
`INBOX.your_folder_name.your_subfolder_name`), choose a model to attach mails
to and a matching algorithm to use.

Exact mailaddress
-----------------

Fill in a field to search for the email address in `Field (model)`. For
partners, this would be `email`. Also fill in the header field from the email
to look at in `Field (email)`. If you want to match incoming mails from your
customers, this would be `from`. You can also list header fields, so to match
partners receiving this email, you might fill in `to,cc,bcc`.

Domain of email addresses
-------------------------

Match the domain of the email address(es) found in `Field (email)`. This would
attach a mail to `test1@example.com` to a record with `Field (model)` set to
`test2@example.com`. Given that this is a fuzzy match, you probably want to
check `Use 1st match`, because otherwise nothing happens if multiple possible
matches are found.

Odoo standard
-------------

This is stricly speaking no matching algorithm, but calls the model's standard
action on new incoming mail, which is usually creating a new record.
