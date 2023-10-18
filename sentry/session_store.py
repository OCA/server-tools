import logging
import os

from odoo import http
from odoo.tools.func import lazy_property

from ..session_redis.session import RedisSessionStore


_logger = logging.getLogger(__name__)

try:
    import redis
    from redis.sentinel import Sentinel
except ImportError:
    redis = None  # noqa
    _logger.debug("Cannot 'import redis'.")

try:
    from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
except ImportError:
    _logger.debug(
        "Cannot import 'sentry-sdk'.\
                        Please make sure it is installed."
    )

sentinel_host = os.environ.get("ODOO_SESSION_REDIS_SENTINEL_HOST")
sentinel_master_name = os.environ.get("ODOO_SESSION_REDIS_SENTINEL_MASTER_NAME")
if sentinel_host and not sentinel_master_name:
    raise Exception(
        "ODOO_SESSION_REDIS_SENTINEL_MASTER_NAME must be defined "
        "when using session_redis"
    )
sentinel_port = int(os.environ.get("ODOO_SESSION_REDIS_SENTINEL_PORT", 26379))
host = os.environ.get("ODOO_SESSION_REDIS_HOST", "localhost")
port = int(os.environ.get("ODOO_SESSION_REDIS_PORT", 6379))
prefix = os.environ.get("ODOO_SESSION_REDIS_PREFIX")
url = os.environ.get("ODOO_SESSION_REDIS_URL")
password = os.environ.get("ODOO_SESSION_REDIS_PASSWORD")
expiration = os.environ.get("ODOO_SESSION_REDIS_EXPIRATION")
anon_expiration = os.environ.get("ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS")
@lazy_property
def session_store():
    if sentinel_host:
        sentinel = Sentinel([(sentinel_host, sentinel_port)], password=password)
        redis_client = sentinel.master_for(sentinel_master_name)
    elif url:
        redis_client = redis.from_url(url)
    else:
        redis_client = redis.Redis(host=host, port=port, password=password)
    return RedisSessionStore(
        redis=redis_client,
        prefix=prefix,
        expiration=expiration,
        anon_expiration=anon_expiration,
        session_class=http.Session,
    )

class CustomSentryWsgiMiddleware(SentryWsgiMiddleware):
    def __init__(self, application):
        super().__init__(application)
        self.session_store = None

    def __call__(self, environ, start_response):
        if self.session_store is None:
            self.session_store = session_store()  # Assuming session_store is supposed to be a method
        return super().__call__(environ, start_response)
