# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from __future__ import annotations

import contextlib
from operator import attrgetter

import numpy as np

from odoo import fields
from odoo.tools import SQL, sql
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
            raise TypeError(
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
            raise TypeError(
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
        if not self.related and (
            not isinstance(self.dimensions, int) or self.dimensions <= 0
        ):
            raise ValueError("The size of the vector field must be a positive integer.")
        return res

    def setup_related(self, model):
        res = super().setup_related(model)
        if not isinstance(self.dimensions, int) or self.dimensions <= 0:
            raise ValueError("The size of the vector field must be a positive integer.")
        return res

    @property
    def _column_type(self):
        if not self.dimensions:
            return None
        return ("vector", f"vector({self.dimensions})")

    def get_current_vector_size(self, cr, table, column):
        """Fetch the current vector size from pg_attribute"""
        query = SQL(
            """
            SELECT format_type(a.atttypid, a.atttypmod)
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace nc ON c.relnamespace = nc.oid
            WHERE nc.nspname = current_schema
              AND c.relname = %s
              AND a.attname = %s
              AND a.attnum > 0
              AND NOT a.attisdropped
            """,
            table,
            column,
        )
        cr.execute(query)
        result = cr.fetchone()
        if result and result[0]:
            type_str = result[0]
            if type_str.startswith("vector(") and type_str.endswith(")"):
                with contextlib.suppress(ValueError):
                    return int(type_str[7:-1])
        return None

    def update_db_column(self, model, column):
        if column:
            db_size = self.get_current_vector_size(
                model.env.cr, model._table, self.name
            )
            if db_size is not None and db_size != self.dimensions:
                sql.convert_column(
                    model.env.cr, model._table, self.name, self.stored_sql_column_type
                )
        return super().update_db_column(model, column)

    _related_dimensions = property(attrgetter("dimensions"))
    _description_dimensions = property(attrgetter("dimensions"))
    _related_autopad = property(attrgetter("autopad"))
    _description_autopad = property(attrgetter("autopad"))

    def convert_to_export(self, value: VectorValue, record):
        return value.to_list() if value else None

    def convert_to_cache(self, value, record, validate=True):
        if (
            value is None
            or value is False
            or (isinstance(value, str) and not value.strip())
        ):
            return None
        if isinstance(value, str):
            clean_str = value.strip()
            try:
                value = [
                    float(x.strip())
                    for x in clean_str.strip("[]()").split(",")
                    if x.strip()
                ]
            except Exception as err:
                raise ValueError(
                    f"Invalid vector string format for {self.name}: '{value}'"
                ) from err
        if not isinstance(value, (list, tuple, np.ndarray, VectorValue)):
            raise TypeError(
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
        if (
            value is None
            or value is False
            or (isinstance(value, str) and not value.strip())
        ):
            return None
        if isinstance(value, str):
            value = self.convert_to_cache(value, record, validate=False)
        if not isinstance(value, (list, tuple, np.ndarray, VectorValue)):
            raise TypeError(
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

    def convert_to_read(self, value, record, use_display_name=True):
        return self.convert_to_export(value, record)

    def convert_to_column(self, value, record, values=None, validate=True):
        return self.convert_to_record(value, record)

    def convert_to_write(self, value, record, values=None):
        return self.convert_to_column(value, record, values)
