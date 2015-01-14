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
