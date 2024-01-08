A widespread configuration is to have a shared mailbox with several folders,
i.e. one where users drop mails they want to attach to partners. Let this
folder be called `From partners`. Then create a folder configuration for your
server with path `"INBOX.From partners"` (note the quotes because of the space,
this is server dependent). Choose model `Partners`, set `Field (model)` to
`email` and `Field (email)` to `from`. In `Domain`, you could fill in
`[('customer', '=', True)]` to be sure to only match customer records.

Now when your users drop mails into this folder, they will be fetched by Odoo
and attached to the partner in question. After some testing, you might want to
check `Delete matches` in your folder configuration so that this folder doesn't
grow indefinitely.
