This module allows you to display all permissions informations of a group or a user.

Group
-----

Displays:

* all inherited/implied groups
* all rules that applies this group and its implied ones
* all access control that applies this group and its implied ones
* all menus accessible from this group and its implied ones
* all views accessible from this group and its implied ones

User
----

Displays:

* aggregation of all the permissions applied to all the groups the user belongs


Pivot views
-----------

This module adds two pivots views on the following objects:

* ``ir.model.access``
* ``ir.rules``

With those pivot views, you can easily extract data to Excel sheet and process it later.
