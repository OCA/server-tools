# -*- coding: utf-8 -*-
# © 2015 Endika Iglesias
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import hashlib
import urllib2

from odoo import api, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_gravatar_base64(self, email=''):
        url = 'https://www.gravatar.com/avatar/{}?s=200'
        _hash = hashlib.md5(email).hexdigest()
        try:
            res = urllib2.urlopen(url.format(_hash))
            raw_image = res.read()
            return base64.encodestring(raw_image)
        except urllib2.HTTPError:
            raise UserError(_('Sorry Gravatar not found.'))

    @api.multi
    def get_gravatar_image(self):
        for rec_id in self:
            email = str(rec_id.email) or ''
            fail_example = self._get_gravatar_base64('fail@email.gravatar')
            user_gravatar = self._get_gravatar_base64(email)
            if fail_example != user_gravatar:
                rec_id.write({'image': user_gravatar})
            else:
                raise UserError(_(
                    "There is no Gravatar image for this email (%s)" % (
                        email
                    )
                ))
        return True
