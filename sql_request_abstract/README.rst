.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================
Abstract Model to manage SQL Requests
=====================================

This module provide an abstract model to manage SQL Select request on database.
It is not usefull for itself. You can see an exemple of implementation in the
'sql_export' module. (same repository).

Implemented features
--------------------

* Add some restrictions in the sql request:
    * you can only read datas. No update, deletion or creation are possible.
    * some tables are not allowed, because they could contains clear password
      or keys. For the time being ('ir_config_parameter').

* The request can be in a 'draft' or a 'SQL Valid' status. To be valid,
  the request has to be cleaned, checked and tested. All of this operations
  can be disabled in the inherited modules.

* This module two new groups:
    * SQL Request / User : Can see all the sql requests by default and execute
      them, if they are valid.
    * SQL Request / Manager : has full access on sql requests.

Usage
=====

Inherit the model:

    from openerp import models

    class MyModel(models.model)
        _name = 'my.model'
        _inherit = ['sql.request.mixin']

        _sql_request_groups_relation = 'my_model_groups_rel'

        _sql_request_users_relation = 'my_model_users_rel'


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Florian da Costa <florian.dacosta@akretion.com>
* Sylvain LE GAL (https://twitter.com/legalsylvain)

Funders
-------

The development of this module has been financially supported by:

* Akretion (<http://www.akretion.com>)
* GRAP, Groupement Régional Alimentaire de Proximité (<http://www.grap.coop>)

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
