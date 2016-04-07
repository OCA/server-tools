# -*- coding: utf-8 -*-
# © 2015 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class NscaServer(models.Model):
    _name = "nsca.server"
    _description = u"NSCA Server"

    name = fields.Char(u"Hostname", required=True)
    port = fields.Integer(u"Port", default=5667, required=True)
    node_hostname = fields.Char(
        u"Hostname of this node", required=True,
        help=u"This is the hostname of the current node declared in the "
             u"monitoring server.")
    config_file_path = fields.Char(
        u"Configuration file", default="/etc/send_nsca.cfg", required=True)
    check_ids = fields.One2many(
        'nsca.check', 'server_id', string=u"Checks")
