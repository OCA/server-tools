# coding: utf-8
# © 2020 Opener B.V. <https://openerp.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2 import sql


def migrate(cr, version):
    """ Fast population of new display_name columns """
    try:
        from openupgradelib import openupgrade
    except ImportError:
        import logging
        logger = logging.getLogger('auditlog.migrations.10.0.1.0.0')
        logger.warn('OpenUpgradelib not available. Quick population of new '
                    'display_name columns not possible.')
        return

    # Fetch the admin user's time zone setting
    cr.execute(
        """SELECT tz FROM res_partner rp
        JOIN ir_model_data imd ON imd.res_id = rp.id
        WHERE imd.module = 'base' AND imd.name = 'user_root'""")
    row = cr.fetchone()
    timezone = row[0] if row and row[0] else 'UTC'

    add_query = "ALTER TABLE {} ADD COLUMN display_name VARCHAR"
    name_query = """\
        UPDATE {} SET display_name = DATE_TRUNC(
            'seconds', create_date at time zone 'UTC' at time zone %s)
            || ' (' ||
            CASE WHEN COALESCE(name, '') != '' THEN name ELSE '?' END
            || ')' """

    for table in ['auditlog_http_request', 'auditlog_http_session']:
        tid = sql.Identifier(table)
        # Precreate column if it does not exist
        if not openupgrade.column_exists(cr, table, 'display_name'):
            cr.execute(sql.SQL(add_query).format(tid))
        # Compose display_name values from create_date cast to the admin
        # user's time zone
        openupgrade.logged_query(
            cr, sql.SQL(name_query).format(tid), (timezone,))
