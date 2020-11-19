# Copyright 2016 Therp BV <https://therp.nl>.
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>.
# Copyright 2018 Ignacio Ibeas <ignacio@acysos.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import os

from odoo import http
from odoo.http import request

from ..models.letsencrypt import _get_challenge_dir


class Letsencrypt(http.Controller):
    @http.route("/.well-known/acme-challenge/<filename>", auth="none")
    def acme_challenge(self, filename):
        try:
            with open(os.path.join(_get_challenge_dir(), filename)) as key:
                return key.read()
        except IOError:
            pass
        return request.not_found()
