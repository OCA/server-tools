# (Copyright) 2015 ABF OSIELL <http://osiell.com>
# (Copyright) 2018 Creu Blanca
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import psutil
import os

from odoo import api, fields, models
from odoo.tools import config


class NscaServer(models.Model):
    _name = "nsca.server"
    _description = u"NSCA Server"

    name = fields.Char(u"Hostname", required=True)
    port = fields.Integer(u"Port", default=5667, required=True)
    password = fields.Char(u"Password")
    encryption_method = fields.Selection(
        selection='_selection_encryption_method',
        string=u"Encryption method", default='1', required=True)
    config_dir_path = fields.Char(
        u"Configuration directory",
        compute='_compute_config_dir_path')
    config_file_path = fields.Char(
        u"Configuration file",
        compute='_compute_config_file_path')
    node_hostname = fields.Char(
        u"Hostname of this node", required=True,
        help=u"This is the hostname of the current Odoo node declared in the "
             u"monitoring server.")
    check_ids = fields.One2many(
        'nsca.check', 'server_id', string=u"Checks")

    def _selection_encryption_method(self):
        return [
            ('0', u"0 - None (Do NOT use this option)"),
            ('1', u"1 - Simple XOR"),
            ('2', u"2 - DES"),
            ('3', u"3 - 3DES (Triple DES)"),
            ('4', u"4 - CAST-128"),
            ('5', u"5 - CAST-256"),
            ('6', u"6 - xTEA"),
            ('7', u"7 - 3WAY"),
            ('8', u"8 - BLOWFISH"),
            ('9', u"9 - TWOFISH"),
            ('10', u"10 - LOKI97"),
            ('11', u"11 - RC2"),
            ('12', u"12 - ARCFOUR"),
            ('14', u"14 - RIJNDAEL-128"),
            ('15', u"15 - RIJNDAEL-192"),
            ('16', u"16 - RIJNDAEL-256"),
            ('19', u"19 - WAKE"),
            ('20', u"20 - SERPENT"),
            ('22', u"22 - ENIGMA (Unix crypt)"),
            ('23', u"23 - GOST"),
            ('24', u"24 - SAFER64"),
            ('25', u"25 - SAFER128"),
            ('26', u"26 - SAFER+"),
        ]

    @api.multi
    def _compute_config_dir_path(self):
        for server in self:
            data_dir_path = config.get('data_dir')
            dir_path = os.path.join(
                data_dir_path, 'nsca_client', self.env.cr.dbname)
            server.config_dir_path = dir_path

    @api.multi
    def _compute_config_file_path(self):
        for server in self:
            file_name = 'send_nsca_%s.cfg' % server.id
            full_path = os.path.join(server.config_dir_path, file_name)
            server.config_file_path = full_path

    @api.multi
    def write_config_file(self):
        for server in self:
            try:
                os.makedirs(server.config_dir_path)
            except OSError as exception:
                if exception.errno != os.errno.EEXIST:
                    raise
            with open(server.config_file_path, 'w') as config_file:
                if server.password:
                    config_file.write('password=%s\n' % server.password)
                config_file.write(
                    'encryption_method=%s\n' % server.encryption_method)
        return True

    @api.multi
    def write(self, vals):
        res = super(NscaServer, self).write(vals)
        self.write_config_file()
        return res

    @api.model
    def create(self, vals):
        res = super(NscaServer, self).create(vals)
        res.write_config_file()
        return res

    @api.model
    def current_status(self):
        ram = 0
        cpu = 0
        if psutil:
            process = psutil.Process(os.getpid())
            # psutil changed its api through versions
            processes = [process]
            if config.get(
                    'workers') and process.parent:  # pragma: no cover
                if hasattr(process.parent, '__call__'):
                    process = process.parent()
                else:
                    process = process.parent
                if hasattr(process, 'children'):
                    processes += process.children(True)
                elif hasattr(process, 'get_children'):
                    processes += process.get_children(True)
            for process in processes:
                if hasattr(process, 'memory_percent'):
                    ram += process.memory_percent()
                if hasattr(process, 'cpu_percent'):
                    cpu += process.cpu_percent(interval=1)
        user_count = 0
        if 'bus.presence' in self.env.registry:
            user_count = self.env['bus.presence'].search_count([
                ('status', '=', 'online'),
            ])
        performance = {
            'cpu': {
                'value': cpu,
            },
            'ram': {
                'value': ram,
            },
            'user_count': {
                'value': user_count,
            },
        }
        return 0, u"OK", performance
