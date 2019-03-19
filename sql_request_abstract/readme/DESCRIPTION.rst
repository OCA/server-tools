This module provides an abstract model to manage SQL Select requests on database.
It is not usefull for itself. You can see an exemple of implementation in the
'sql_export' module. (same repository).

Implemented features
~~~~~~~~~~~~~~~~~~~~

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
