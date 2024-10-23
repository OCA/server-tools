This module is a technical module for developpers.

It adds a new decorator, named ``@api.allowed_groups``.

- When the function is executed, it checks if the user belong to one of the given groups.

- It also adds automatically group(s) in the according form views to hide
  buttons if the user doesn't belong to one of the given groups.

Interests
---------

It makes the application more secure and more concise, the developer only has to write the accreditation level in one place, instead of writing it twice (once in the XML view, and the other time in the python code)

In Odoo, there are many places where an action is hidden in the Form view, but the function can be called in particular by XML-RPC calls, that makes a lot a security issue, included
in recent version.

Ref : https://github.com/odoo/odoo/pull/66505
