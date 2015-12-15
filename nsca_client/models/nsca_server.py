# -*- coding: utf-8 -*-
# © 2015 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class NscaServer(models.Model):
    _name = "nsca.server"
    _description = u"NSCA Server"

    name = fields.Char(u"Hostname", required=True)
    port = fields.Integer(u"Port", default=5667, required=True)
    check_ids = fields.One2many(
        'nsca.check', 'server_id', string=u"Checks")
