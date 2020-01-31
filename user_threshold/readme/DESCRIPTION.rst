This module adds the ability to limit the amount of non-portal/public
users that exist in the database and per-company.

It adds a group named `User Threshold Managers` which are  the only users
who can alter the thresholds.

This module also limits the  ability of users to add membership
to the manager group to  pre-existing members. By default, `Administrator` 
is the only member of this group.

Additionally, there is a flag that can be set on users so that they do not
count towards the user threshold.

Using the `USER_THRESHOLD_HIDE` environment variable, you can also hide the 
threshold exemption flag from users and the company setting for user 
threshold. Setting this flag will also remove threshold exemptions for any 
users who are not defined in the `USER_THRESHOLD_USER` environment variable.

There are two modules available that also implement functionality similar to
what is provided in this module but in a more abstract way. They are:

https://github.com/it-projects-llc/access-addons/tree/10.0/access_limit_records_number
https://github.com/it-projects-llc/access-addons/tree/10.0/access_restricted
