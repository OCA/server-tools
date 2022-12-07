# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


# Monkey patch odoo method in order to track all database


import logging

import psycopg2

import odoo.http
from odoo.sql_db import Cursor

from odoo.addons.base.models.ir_cron import ir_cron

_logger = logging.getLogger(__name__)
HAS_SENTRY_SDK = True

try:
    from sentry_sdk import start_transaction
    from sentry_sdk.hub import Hub
    from sentry_sdk.tracing_utils import record_sql_queries
except ImportError:  # pragma: no cover
    HAS_SENTRY_SDK = False  # pragma: no cover
    _logger.debug(
        "Cannot import 'sentry-sdk'.\
                        Please make sure it is installed."
    )  # pragma: no cover


if HAS_SENTRY_SDK:

    _ori_get_request = odoo.http.Root.get_request

    def get_request(self, httprequest):
        request = _ori_get_request(self, httprequest)
        hub = Hub.current
        with hub.configure_scope() as scope:
            # Extract some params of the request to give a better name
            # to the transaction and also add tag to improve filtering
            # experience on sentry
            scope.set_transaction_name(httprequest.environ.get("PATH_INFO"))
            scope.set_user({"id": httprequest.session.get("uid")})
            for key in ["model", "method"]:
                if key in request.params:
                    scope.set_tag(f"odoo.{key}", request.params[key])
            scope.set_tag("odoo.db", request.db)
        return request

    odoo.http.Root.get_request = get_request

    _ori_execute = Cursor.execute

    def execute(self, query, params=None, log_exceptions=None):
        with record_sql_queries(
            Hub.current, self, query, params, psycopg2.paramstyle, executemany=False
        ):
            return _ori_execute(
                self, query, params=params, log_exceptions=log_exceptions
            )

    Cursor.execute = execute

    _ori_process_job = ir_cron._process_job

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):
        with start_transaction(
            op="cron", name=f"Cron {job['cron_name']}".replace(" ", "_")
        ) as transaction:
            transaction.set_tag("odoo.db", job_cr.dbname)
            return _ori_process_job(job_cr, job, cron_cr)

    ir_cron._process_job = _process_job

    try:
        from odoo.addons.queue_job.controllers.main import RunJobController

        _ori_try_perform_job = RunJobController._try_perform_job

        def _try_perform_job(self, env, job):
            hub = Hub.current
            with hub.configure_scope() as scope:
                scope.set_tag("odoo.job.model", job.model_name)
                scope.set_tag("odoo.job.method", job.method_name)

            return _ori_try_perform_job(self, env, job)

        RunJobController._try_perform_job = _try_perform_job
    except ImportError:  # pragma: no cover
        _logger.debug("Queue Job not install skip instrumentation")  # pragma: no cover
