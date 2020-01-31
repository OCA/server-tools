A system parameter named `user.threshold.database` is added by default with 
the value of '0' (Unlimited). Set this value to the total number of users 
you wish to allow in the database.

A field has been added to users to allow you to exempt them from the 
thresholds.

A field has been added to all companies, which allows you to define the max 
number of users that the company can have.

The following environment variables are available for your configuration ease:

+---------------------+--------------------------------------------------------+
| Name                | Description                                            |
+=====================+========================================================+
| USER_THRESHOLD_HIDE | Hide all threshold settings and default the exempt     |
|                     | users to those defined by the ``USER_THRESHOLD_USERS`` |
|                     | variable.                                              |
+---------------------+--------------------------------------------------------+
| USER_THRESHOLD_USER | White list of users who are exempt from the threshold. |
+---------------------+--------------------------------------------------------+
