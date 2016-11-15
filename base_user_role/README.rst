.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========
User roles
==========

This module was written to extend the standard functionality regarding users
and groups management.
It helps creating well-defined user roles and associating them to users.

It can become very hard to maintain a large number of user profiles over time,
juggling with many technical groups. For this purpose, this module will help
you to:

  * define functional roles by aggregating low-level groups,
  * set user accounts with the predefined roles (roles are cumulative),
  * update groups of all relevant user accounts (all at once),
  * ensure that user accounts will have the groups defined in their roles
    (nothing more, nothing less). In other words, you can not set groups
    manually on a user as long as there is roles configured on it,
  * activate/deactivate roles depending on the date (useful to plan holidays, etc)
  * get a quick overview of roles and the related user accounts.

That way you make clear the different responsabilities within a company, and
are able to add and update user accounts in a scalable and reliable way.

Configuration
=============

To configure this module, you need to go to *Configuration / Users / Roles*,
and create a new role. From there, you can add groups to compose your role,
and then associate users to it.

Roles:

.. image:: /base_user_role/static/description/roles.png

Add groups:

.. image:: /base_user_role/static/description/role_groups.png

Add users (with dates or not):

.. image:: /base_user_role/static/description/role_users.png

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Oxygen Team: `Icon <http://www.iconarchive.com/show/oxygen-icons-by-oxygen-icons.org/Actions-user-group-new-icon.html>`_ (LGPL)

Contributors
------------

* Sébastien Alix <sebastien.alix@osiell.com>

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
