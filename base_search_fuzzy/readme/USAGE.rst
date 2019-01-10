#. You can create an index for the `name` field of `res.partner`.
#. In the search you can use:

   ``self.env['res.partner'].search([('name', '%', 'Jon Miller)])``

#. In this example the function will return positive result for `John Miller`
   or `John Mill`.

#. You can tweak the number of strings to be returned by adjusting the set
   limit (default: 0.3). NB: Currently you have to set the limit by executing
   the following SQL statement:

   ``self.env.cr.execute("SELECT set_limit(0.2);")``

#. Another interesting feature is the use of ``similarity(column, 'text')``
   function in the ``order`` parameter to order by similarity. This module just
   contains a basic implementation which doesn't perform validations and has to
   start with this function. For example you can define the function as
   followed:

   ``similarity(%s.name, 'John Mil') DESC" % self.env['res.partner']._table``

For further questions read the Documentation of the
`pg_trgm <https://www.postgresql.org/docs/current/static/pgtrgm.html>`_ module.
