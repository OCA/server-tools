
> **⚠️ Warning**  
> This addon is **not compatible** with the Python `pgvector` library. Please ensure that you do not use this library alongside the addon to avoid potential issues. This is mainly due to the fact that numpy arrays can't be stored into the odoo cache since they are not comparable with the default '==' or '!=' operators.

The module is a technical module providing a new field type called "Vector". It's intended to be used by developers who want to store and manage vector data in their Odoo database when they develop their own modules.

## Field declaration

To declare a field of type vector, you can use the following syntax:

```python

from odoo.addons.field_vector.fields import Vector


class YourModel(models.Model):
    _name = 'your.model'

    vector_field = Vector(dimensions=3)
```

The `dimensions` parameter is required and specifies the number of dimensions of the vector. The field will be stored as a `vector` type in PostgreSQL, which is a native type for storing vectors.

By default the field is declared as no `prefetch=False` and with `autopad=True`.
You can override these parameters by passing them as arguments to the field:

```python
from odoo.addons.field_vector.fields import Vector
class YourModel(models.Model):
    _name = 'your.model'

    vector_field = Vector(dimensions=3, prefetch=True, autopad=False)
```

The `prefetch` parameter allows you to enable or disable prefetching of the field when loading records. If set to `True`, the field will be prefetched when loading records, which can improve performance when accessing the field frequently. If set to `False`, the field will not be prefetched, which can save memory and improve performance when accessing the field infrequently (which would be the common case).

The `autopad` parameter allows you to enable or disable automatic padding of the vector when storing it in the database. If set to `True`, the vector will be automatically padded with zeros to match the specified dimensions. If set to `False`, the vector will not be padded but if the vector is shorter than the specified dimensions an error will be raised.

## Field usage

The vector field can be used like any other field in Odoo. When accessing the field, it will always return an `odoo.addons.field_vector.fields.VectorValue` object, which is a wrapper around value stored into the database. This object
provides a convenient way to get the value of the vector as a numpy array.

```python
import numpy as np
from odoo.addons.field_vector.fields import  VectorValue

record = self.env['your.model'].create({
    'vector_field': [1.0, 2.0, 3.0]
})

assert isinstance(record.vector_field, VectorValue)
assert isinstance(record.vector_field.value, np.ndarray)

```

When setting the field, you can pass a list of values or a numpy array or a `VectorValue` object or a list/tuple of values. The field will automatically convert the value to a VectorValue and store it in the database into the vector format.

```python

record.vector_field = [1.0, 2.0, 3.0]
assert isinstance(record.vector_field, VectorValue)

record.vector_field = np.array([1.0, 2.0, 3.0])
assert isinstance(record.vector_field, VectorValue)

record.vector_field = VectorValue([1.0, 2.0, 3.0])
assert isinstance(record.vector_field, VectorValue)

```

## Plain SQL queries

When reading the field in plain SQL queries, the field will be returned as a
`VectorValue` object. You can use the `value` property to get the value of the vector as a numpy array.

```python

env.cr.execute('SELECT vector_field FROM your_model WHERE id = 1')
record = env.cr.fetchone()
vector_value = record[0]
assert isinstance(vector_value, VectorValue)
```

When writing the field in plain SQL queries, you can pass a numpy array or a list of values or a VectorValue object as the value of the field (in this specific case tuples are not supported).

```python

env.cr.execute('UPDATE your_model SET vector_field = %s WHERE id = 1', (np.array([1.0, 2.0, 3.0]),))
env.cr.execute('UPDATE your_model SET vector_field = %s WHERE id = 1', ([1.0, 2.0, 3.0],))
env.cr.execute('UPDATE your_model SET vector_field = %s WHERE id = 1', (VectorValue([1.0, 2.0, 3.0]),))

```
