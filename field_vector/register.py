# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import numpy as np
from psycopg2.extensions import adapt, new_type, register_adapter, register_type

from .fields import VectorValue

_is_vector_type_registered = False


class VectorAdapter:
    def __init__(self, value):
        self._value = value

    def getquoted(self):
        return adapt(VectorValue._to_db(self._value)).getquoted()


def cast_vector(value, cur):
    return VectorValue._from_db(value)


def register_vector(cr):
    global _is_vector_type_registered
    if _is_vector_type_registered:
        return
    cr.execute("SELECT typname, oid FROM pg_type WHERE oid = to_regtype('vector')")
    type_info = dict(cr.fetchall())
    if "vector" not in type_info:
        raise ValueError("vector type not found in the database")

    vector = new_type((type_info["vector"],), "VECTOR", cast_vector)
    register_type(vector)
    register_adapter(np.ndarray, VectorAdapter)
    register_adapter(VectorValue, VectorAdapter)
    _is_vector_type_registered = True
