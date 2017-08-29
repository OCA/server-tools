.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

==============
User Threshold
==============

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


Usage
=====

A system parameter named `user.threshold.database` is added by default with 
the value of '0' (Unlimited). Set this value to the total number of users 
you wish to allow in the database.

A field has been added to users to allow you to exempt them from the 
thresholds.

A field has been added to all companies, which allows you to define the max 
number of users that the company can have.

The following environment variables are available for your configuration ease:

| Name | Description |
|------|-------------|
| USER_THRESHOLD_HIDE | Hide all threshold settings and default the exempt users to those defined by the USER_THRESHOLD_USERS variable
| USER_THRESHOLD_USER | White list of users who are exempt from the threshold.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
`<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Ted Salmon <tsalmon@laslabs.com>
* Dave Lasley <dave@laslabs.com>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
