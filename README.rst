Fetch mails into inbox
======================

In some cases, you may not want to have OpenERP create objects directly
on mail arrival, but put them into an inbox for further (possibly manual)
processing.

This module provides the base for this workflow and elementary UI for
processing.

Usage
-----

Create a fetchmail configuration and use 'Fetchmail inbox' as object to be
created on mail arrival. Be sure to check Advanced/Keep original in order
not to lose data in the intermediate step via the inbox.

Mails fetched from this configuration end up in
Settings/Technical/Email/Fetchmail Inbox,
where they can be reviewed and eventually used to create new objects or
attached to existing objects.

Further development
-------------------

This module deals with emails in a very generic way, which is good for
flexibility, but bad for usability. Fortunately, it was developed with
extensibility in mind so that it is very simple to write extension modules
to ease handling emails for specific models in a more user friendly manner.

In simple cases, if you want to force specifying objects of just one model,
you can put 'set_default_res_model': 'your.model' into the menu action's
context and you're done.

Credits
-------

* icon courtesy of http://fortawesome.github.io/Font-Awesome/icon/inbox/

Contributors
============

* Holger Brunn <hbrunn@therp.nl>
* Stefan Rijnhart <stefan@opener.amsterdam>
