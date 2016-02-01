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
            return file_open(
                os.path.join('letsencrypt', 'static', 'acme-challenge',
                             filename)
            ).read()
        except IOError:
            pass
        return request.not_found()
