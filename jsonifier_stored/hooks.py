# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

# This script is not meant to be used as is.
# Use it in your module in a pre init hook
# in order to add the `jsonified_data` column
# before the installation of the module,
# in order to avoid the computation,
# which might be slow.
from psycopg2 import sql


def add_jsonifier_column(cr, table_name):
    query = sql.SQL(
        "ALTER TABLE {table_name} " "ADD COLUMN IF NOT EXISTS jsonified_data TEXT;"
    ).format(table_name=sql.Identifier(table_name))
    cr.execute(query)
