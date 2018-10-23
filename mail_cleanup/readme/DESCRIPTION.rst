This module allows to:
----------------------

* mark e-mails older than x days as read,
* move those messages in a specific folder,
* remove messages older than x days
  on IMAP servers, just before fetching them.

Since the main "mail" module does not mark unroutable e-mails as read,
this means that if junk mail arrives in the catch-all address without
any default route, fetching newer e-mails will happen after re-parsing
those unroutable e-mails.
