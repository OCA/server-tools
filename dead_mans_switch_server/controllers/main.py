# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import werkzeug
from openerp import http
from openerp.http import request


class Main(http.Controller):
    @http.route('/dead_mans_switch/alive', type='json', auth="none")
    def alive(self, **kwargs):
        if 'database_uuid' not in kwargs:
            raise werkzeug.exceptions.NotFound()
        instance = request.env['dead.mans.switch.instance'].sudo().search([
            ('database_uuid', '=', kwargs['database_uuid']),
        ])
        if not instance:
            instance = request.env['dead.mans.switch.instance'].sudo().create({
                'database_uuid': kwargs['database_uuid'],
            })
        data = {
            field: value
            for field, value in kwargs.iteritems()
            if field in request.env['dead.mans.switch.log']._fields
        }
        instance.write({
            'log_ids': [(0, 0, data)],
        })
