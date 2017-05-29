# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# pragma: no-cover


def migrate(cr, version):
    """Update database from previous versions, before updating module."""
    cr.execute(
        "ALTER TABLE custom_info_value RENAME COLUMN value TO value_str")
