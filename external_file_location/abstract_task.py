# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from base64 import b64encode


class AbstractTask(object):

    _name = None
    _key = None
    _synchronize_type = None
    _default_port = None
    _hide_login = False
    _hide_password = False
    _hide_port = False

    def create_file(self, filename, data):
        ir_attachment_id = self.env['ir.attachment.metadata'].create({
            'name': filename,
            'datas': b64encode(data),
            'datas_fname': filename,
            'task_id': self.task and self.task.id or False,
            'location_id': self.task and self.task.location_id.id or False,
            'external_hash': self.ext_hash
            })
        return ir_attachment_id
