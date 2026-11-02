This module formats phone numbers automatically when a contact is edited or
saved, so that every number in the database follows the same format.

* Numbers are reformatted as soon as the user leaves the field, and again on
  save (including imports and API calls).
* Every stored text field whose technical name contains ``phone`` or
  ``mobile`` is handled, including custom fields added with Studio.
* One field may hold several numbers, separated by a comma, a semicolon or a
  new line. Each number is formatted on its own.
* Numbers that cannot be parsed are left exactly as typed.

It relies on the ``phone_validation`` module and the ``phonenumbers`` Python
library.
