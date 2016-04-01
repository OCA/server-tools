# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
from openerp import http
from openerp.http import request
from openerp.tools.misc import file_open


class Letsencrypt(http.Controller):
    @http.route('/.well-known/acme-challenge/<filename>', auth='none')
    def acme_challenge(self, filename):
        try:
            with file(
                os.path.join(request.env['letsencrypt'].get_challenge_dir(),
                             filename)
            ) as challenge:
                return challenge.read()
        except IOError:
            pass
        return request.not_found()
