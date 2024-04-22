# Copyright 2016,2022 Therp BV <https://therp.nl>.
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>.
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=too-few-public-methods,no-self-use
"""This controller handles the acme challenge call from Letsencrypt."""
import logging
import os

from odoo import _, http
from odoo.http import request

from ..models.letsencrypt import _get_challenge_dir

_logger = logging.getLogger(__name__)


class Letsencrypt(http.Controller):
    """This controller handles the acme challenge call from Letsencrypt."""

    @http.route("/.well-known/acme-challenge/<filename>", auth="none")
    def acme_challenge(self, filename):
        """Handle the acme challenge."""
        path = os.path.join(_get_challenge_dir(), filename)
        try:
            with open(path, encoding="utf-8") as key:
                return key.read()
        except IOError:
            _logger.exception(_("Error opening file %s"), path)
        raise request.not_found()
