# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from __future__ import annotations

from operator import attrgetter

import numpy as np
from psycopg2.extensions import AsIs

from odoo import fields
from odoo.tools import sql
from odoo.tools.misc import SENTINEL, Sentinel


class VectorValue:
    """
    Class to represent a vector value.
    This class as a wrapper around the text representation of the vector
    to allow for easy manipulation and conversion to/from other formats.

    It's designed to be put in the record's cache and returned as record's value.
    It's also used when the database is queried to convert the value to/from
    the database format in a transparent way.
    """

    def __init__(self, value: list | tuple | np.ndarray, dimensions=None, autopad=True):
        if not isinstance(value, (list, tuple, np.ndarray)):
            raise ValueError(
                f"Invalid type '{type(value)}' for VectorValue: "
                "Only list, tuple or np.ndarray are allowed."
            )
        if isinstance(value, np.ndarray):
            if value.dtype != ">f4":
                value = value.astype(">f4")
            value = value.tolist()
        self._value = value
        if dimensions is not None and len(value) != dimensions and autopad:
            self.pad(dimensions)

    def __repr__(self):
        return f"VectorValue({self._value})"

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, self.__class__):
            return np.array_equal(self._value, value._value)
        return False

    def __len__(self):
        return len(self._value)

    def to_list(self):
        """
        Convert the vector value to a list.
        """
        return list(self._value)

    def pad(self, dimensions: int):
        """
        Pad the vector value to the given size.
        """
        if len(self._value) < dimensions:
            self._value = [*self._value, *([0] * (dimensions - self.dimensions))]
        return self

    @property
    def value(self):
        """
        Return the value as a numpy array.
        """
        return np.asarray(self._value, dtype=">f4")

    @property
    def dimensions(self):
        """
        Return the dimensions of the vector.
        """
        return len(self._value)

    @classmethod
    def _from_db(cls, value: str) -> VectorValue:
        """
        Convert a binary value from the database to a VectorValue.
        """
        if value is None:
            return None
        return cls([float(v) for v in value[1:-1].split(",")])

    @classmethod
    def _to_db(cls, value: list | tuple | np.ndarray | VectorValue) -> str:
        """
        Convert a VectorValue to a binary value for the database.
        """
        if value is None:
            return None
        if isinstance(value, list | tuple | np.ndarray):
            value = cls(value)
        if not isinstance(value, cls):
            raise ValueError(
                f"Invalid type '{type(value)}' for VectorValue: "
                "Only list, tuple or np.ndarray or VectoreValue are allowed."
            )
        return "[" + ",".join([str(float(v)) for v in value.value]) + "]"


class Vector(fields.Field):
    """
    Specialized field to store vector data.
    This field is based on the pgvector extension for PostgreSQL.
    It allows to store and manipulate vector data efficiently.

    This field can be used to store vectors of any size.
    The dimension of the vector is defined at the field level.

    By default, the field is not pre-fetched.
    To ease the use of the field, it is automatically padded to the size of the vector.


    """

    type = "vector"
    dimensions = None
    prefetch = False
    autopad = True

    def __init__(
        self,
        dimensions: int | Sentinel = SENTINEL,
        autopad: bool | Sentinel = SENTINEL,
        string: str | Sentinel = SENTINEL,
        **kwargs,
    ):
        super().__init__(
            dimensions=dimensions, string=string, autopad=autopad, **kwargs
        )

    def _setup_attrs__(self, model_class, name):
        res = super()._setup_attrs__(model_class, name)
        if not isinstance(self.dimensions, int) or self.dimensions <= 0:
            raise ValueError("The size of the vector field must be a positive integer.")
        return res

    @property
    def _column_type(self):
        return ("vector", f"vector({self.dimensions})")

    def get_current_vector_size(self, cr, table, column):
        """Fetch the current vector size from pg_typeof()"""
        cr.execute(
            "SELECT pg_typeof(%s)::text FROM %s LIMIT 1;", (AsIs(column), AsIs(table))
        )
        result = cr.fetchone()
        if result and result[0] == "vector":
            cr.execute(
                "SELECT vector_dims(%s) FROM %s"
                " WHERE vector_dims(%s) IS NOT NULL LIMIT 1;",
                (AsIs(column), AsIs(table), AsIs(column)),
            )
            result = cr.fetchone()
            if result and result[0]:
                return int(result[0])
        return None

    def update_db_column(self, model, column):
        if column:
            db_size = self.get_current_vector_size(
                model.env.cr, model._table, self.name
            )
            if db_size is not None and db_size != self.dimensions:
                sql.convert_column(
                    model.env.cr, model._table, self.name, self._column_type[1]
                )
        return super().update_db_column(model, column)

    _related_dimensions = property(attrgetter("dimensions"))
    _description_dimensions = property(attrgetter("dimensions"))

    def convert_to_export(self, value: VectorValue, record):
        return value.to_list() if value else None

    def convert_to_cache(self, value, record, validate=True):
        if value is None or value is False:
            return None
        if not isinstance(value, (list, tuple, np.ndarray, VectorValue)):
            raise ValueError(
                f"Invalid type '{type(value)}' for {self.name}: "
                "Only np.ndarray or list of floats/int are allowed."
            )
        if not isinstance(value, VectorValue):
            value = VectorValue(value, dimensions=self.dimensions, autopad=self.autopad)
        if self.autopad and value.dimensions < self.dimensions:
            value = value.pad(self.dimensions)
        if validate and value.dimensions != self.dimensions:
            raise ValueError(
                f"Invalid vector size for {self.name}: {value.dimensions} != "
                f"{self.dimensions}"
            )
        return value

    def convert_to_record(self, value, record):
        if value is None or value is False:
            return None
        if not isinstance(value, (list, tuple, np.ndarray, VectorValue)):
            raise ValueError(
                f"Invalid type '{type(value)}' for {self.name}: "
                "Only np.ndarray, list of floats/int or VectorValue are allowed."
            )
        if not isinstance(value, VectorValue):
            value = VectorValue(value, dimensions=self.dimensions, autopad=self.autopad)
        if self.autopad and value.dimensions < self.dimensions:
            value = value.pad(self.dimensions)
        if value.dimensions != self.dimensions:
            raise ValueError(
                f"Invalid vector dimensions for {self.name}: "
                "{value.dimensions} != {self.dimensions}"
            )
        return value

    def convert_to_read(self, value, record, use_name_get=True):
        return self.convert_to_export(value, record)

    def convert_to_column(self, value, record, values=None, validate=True):
        return self.convert_to_record(value, record)

    def convert_to_write(self, value, record, values=None):
        return self.convert_to_column(value, record, values)
