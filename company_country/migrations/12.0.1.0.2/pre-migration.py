import logging
from psycopg2.extensions import AsIs

from odoo import tools


_logger = logging.getLogger(__name__)


def migrate(cr, version):
    drop_table_model_company_country(cr)


def drop_table_model_company_country(cr):
    tablename = 'company_country_config_settings'
    if tools.table_exists(cr, tablename):
        _logger.info("Dropping table %s", tablename)
        cr.execute("DROP TABLE IF EXISTS %s;", (AsIs(tablename),))
