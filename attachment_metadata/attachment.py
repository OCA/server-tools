# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright 2011-2012 Camptocamp SA
#   @author: Joel Grand-Guillaume
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import hashlib
from base64 import b64decode


class IrAttachmentMetadata(models.Model):
    _name = 'ir.attachment.metadata'
    _inherits = {'ir.attachment': 'attachment_id'}

    internal_hash = fields.Char(store=True, compute='_compute_hash')
    external_hash = fields.Char()
    attachment_id = fields.Many2one('ir.attachment', required=True,
                                    ondelete='cascade')

    @api.depends('datas', 'external_hash')
    def _compute_hash(self):
        if self.datas:
            self.internal_hash = hashlib.md5(b64decode(self.datas)).hexdigest()
        if self.external_hash and self.internal_hash != self.external_hash:
            raise Warning(_('File corrupted'),
                          _("Something was wrong with the retreived file, "
                              "please relaunch the task."))
