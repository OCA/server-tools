from odoo import _
from odoo.exceptions import UserError

try:
    from clickhouse_driver import Client as ClickHouseClient
except ImportError:
    ClickHouseClient = None


def _require_driver() -> None:
    """Ensure clickhouse-driver is available in the current environment.

    :raises UserError: If clickhouse-driver is not installed.
    """
    if ClickHouseClient is None:
        raise UserError(
            _(
                "Python package 'clickhouse-driver' is not available. "
                "Install it in the Odoo environment to use ClickHouse storage."
            )
        )


def get_clickhouse_client(
    *,
    host,
    port,
    database,
    user,
    password=None,
    settings=None,
) -> "ClickHouseClient":
    """Create and return a clickhouse-driver Client instance.

    Uses native TCP protocol.

    :param host: ClickHouse hostname or IP
    :type host: str
    :param port: Native TCP port
    :type port: int
    :param database: Default database
    :type database: str
    :param user: ClickHouse username
    :type user: str
    :param password: ClickHouse password, optional
    :type password: Optional[str]
    :param settings: Optional clickhouse-driver settings mapping
    :type settings: Optional[Mapping[str, Any]]
    :return: Configured ClickHouse client
    :rtype: clickhouse_driver.Client
    :raises UserError: If clickhouse-driver is not installed
    """
    _require_driver()
    # `settings` is passed as-is to clickhouse-driver, keep it optional and immutable.
    return ClickHouseClient(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password or "",
        settings=dict(settings or {}),
    )
