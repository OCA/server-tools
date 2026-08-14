This module disables the indexation of attachments content.

Attachment model has a field called 'index_content' where the content of
the attachment is read and stored directly in the database. This field
is useful in order to search content of a file. But most of cases it is
not used, so, you can install this module in order to:

- **Avoid Duplicating Data:** Because indexation extracts text content
  from files and put it on the database in order it could be searched,
  but this implies you have the file data in your `filestore` directory,
  and also part (or sometimes all) of that data in your database too.
- **Improve Performance:** Since not all indexed files are plain text,
  they require extra process to read them.

Maybe you could try to uninstall modules like `document` in order to
disable its indexation features, but you could face the uninstallation
of other modules that could be useful for you (e.g, `hr_recruitment`
depends on that).

But even if you don't have `document` installed, you'd still have plain
text content indexation by default. As you can see in this SQL query
results, indexation is active even without it:

[![SQL Query result showing indexed content](https://user-images.githubusercontent.com/442938/67894113-45d27a80-fb2e-11e9-9a22-ba43d8b444c5.png)](https://user-images.githubusercontent.com/442938/67894113-45d27a80-fb2e-11e9-9a22-ba43d8b444c5.png)

Using this module you will not require to uninstall any module to
disable the attachment content indexation, because we directly disable
it at `ir.attachment` base.

Also, after the installation, the `index_content` field on attachments
already recorded in database will be cleared.
