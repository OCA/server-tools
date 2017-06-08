# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
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
from openerp.osv import orm


class mail_compose_message(orm.Model):
    """Patch mail.compose.message to add attachment_ids (given as
    default_attachment_ids in context) to email template."""
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, cr, uid, ids, template_id, composition_mode,
                             model, res_id, context=None):
        res = super(mail_compose_message, self).\
            onchange_template_id(cr, uid, ids, template_id, composition_mode,
                                 model, res_id, context)
        if 'default_attachment_ids' in context:
            res['value']['attachment_ids'] = context['default_attachment_ids']
        return res
