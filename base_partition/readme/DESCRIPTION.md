This module adds a partition(self, accessor) method to every model. It
accepts for accessor any parameter that would be accepted by mapped,
i.e. a string "field(.subfield)\*" or a function (lambda x: not x.b). It
returns a dictionary with keys that are equal to
set(record.mapped(accessor)), and with values that are recordsets (these
recordsets forming a partition of the initial recordset, conveniently).

So if we have a recordset (x \| y \| z ) such that x.f == True, y.f ==
z.f == False, then (x \| y \| z ).partition("f") == {True: x, False: (y
\| z)}.
