# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Business Applications
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class TransbotLog(models.Model):
    _name = 'transbot.log'
    _recname = 'date'
    _order = 'date desc'

    date = fields.Datetime(string="Date", required=True)
    log = fields.Char(string="Log message", required=True)
    project = fields.Many2one(comodel_name="transbot.project",
                              string="Github project reference", readonly=True,
                              ondelete="cascade")
    type = fields.Selection([('info', 'INFO'),
                             ('debug', 'DEBUG'),
                             ('error', 'ERROR')], string="Type",
                            required=True, default='info')

    def log_message(self, log, date=False, log_type='info', project=False):
        if not date:
            date = fields.Datetime.now()
        return self.create({'date': date,
                            'log': log,
                            'type': log_type,
                            'project': project})
