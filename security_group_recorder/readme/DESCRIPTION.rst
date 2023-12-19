This module allows to record the security workflow of the active user,
and then propose a user group based on that recording.

All permissions recorded during the user's workflow, but that are included
in the default Internal User security group and it's inherited groups, will not be
taken into consideration.

When the user stops recording his workflow, a new user group proposal will pop up.
The user will be able to customize, if desired, the proposed configuration and then create
the security group from there. The user can also discard the security group proposal and
begin another recording.

It is important to mention that this module creates an approximation of the required user
group. The accuracy of the approximation improves with more precise tracking of user
actions. Certain access rights to technical models may not be recorded because Odoo
generates many of them, leading to potential noise in various cases.
