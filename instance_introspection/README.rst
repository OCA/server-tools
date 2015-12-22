VauxooMin4 Tools.
=================

This module is part of VauxooMin Tools.

Used to know state of your server instance, to improve the quality of services
it shows information about all branches setted in your addons_path config.

Features.
---------

Add a new menu, This menu named is ``Branch Info``, you
need belong to "Access Rights" group to be able to see it.

This menu call an action windows that show a button with Load Info string,
press it to load information about your branchs set in your server
configuration.

Functional Information.
-----------------------

This show in a Kanban view the following information:

    - Branch's name (known as nick).
    - Absolute path of the branch in your server.
    - Last reviewer branch.
    - Revno Branch.
    - Parent branch that we are getting the pull from.

This information is shown in colors, and each color has a meaning which is:

    - Blue: If there are changes without commits in the branch
    - Red: If path is not a branch
    - Green: If all is correctly in this branch.

.. image:: branch_info/static/src/img/branch_info.png

TODO: may be add git support?