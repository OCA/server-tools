Negativ Groups
==============

Now you can use negative groups in the backend and front-end.
Right now it is only possible to have positive groups in odoo.


Example:
--------


* <div groups="portal.group_read">

       <button name="def_read" string="Button 1" />

  </div>
* <div groups="not portal.group_read">

       <button name="def_read_and_edit" string="Button 2" />

  </div>

You have a menu, button or field which will be seen by members of a specific group, but you want to place a slightly different menu, button or field with a different option and you want that this button is shown for users which are not in that specific group. 

You don't want to place a lot of buttons for several groups because you want all groups beside the first one. 

Now you have the possibility to use negative groups in the Backend which means all other groups will see this content. 

Credits
=======

Contributors
------------

* Benjamin Bachmann (benniphx@gmail.com)
* Robert Rübner (rruebner@bloopark.de)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png

:alt: Odoo Community Association
:target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.