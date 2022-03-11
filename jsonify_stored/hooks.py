# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

# This script is not meant to be used as is.
# Add it in your module in order to add the `jsonified_data` column
# before the installation of the module, in order to avoid the computation,
# which might be slow.


def add_jsonify_column(cr, table_name):
    query = f"""
        ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS jsonified_data TEXT;
    """
    cr.execute(query)
