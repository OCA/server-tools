* Write tests.

* Add a warning, if groups defined in decorator are not the same as
  group defined in the view.
  (remarks https://github.com/OCA/server-tools/pull/2026#discussion_r579102673)

Theoritical Limitation
----------------------

* Due to current limitation of the ``_get_final_method`` function, you can not
  decorate a function if the class contains other functions with the same name,
  but other argument list.
