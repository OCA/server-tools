Description
-----------
This module allows defining groups whose membership is a condition expressed as
python code. For every user, it is evaluated during login if she belongs to
the group or not.

Usage
-----
Check `Dynamic` on a group you want to be dynamic. Now fill in the condition,
using `user` which is a browse record of the user in question that evaluates
truthy if the user is supposed to be a member of the group and falsy if not.

There is a constraint on the field to check for validity if this expression.
When you're satisfied, click the button `Evaluate` to prefill the group's
members. The condition will be checked now for every user who logs in.

Example
-------
We have a group called `Amsterdam` and want it to contain all users from
city of Amsterdam. So we use the membership condition

.. code:: python

   user.partner_id.city == 'Amsterdam'

Now we can be sure every user living in this city is in the right group, and we
can start assigning local menus to it, adjust permissions, etc. Keep in mind
that view overrides can also be restricted by a group id, this gives a lot of
possibilities to dynamically adapt views based on arbitrary properties
reachable via the user record.
