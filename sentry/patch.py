# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


# Monkey patch odoo method in order to track all database


import logging

import odoo.http

_logger = logging.getLogger(__name__)
HAS_SENTRY_SDK = True

try:
    from sentry_sdk.hub import Hub
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
