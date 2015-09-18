# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
import base64
import hashlib
import urllib2


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_gravatar_base64(self, email=''):
        url = 'http://www.gravatar.com/avatar/{}?s=200'
        _hash = hashlib.md5(email).hexdigest()
        try:
            res = urllib2.urlopen(url.format(_hash))
            raw_image = res.read()
            return base64.encodestring(raw_image)
        except urllib2.HTTPError:
            raise Warning(_('Sorry Gravatar not found.'))

    @api.one
    def get_gravatar_image(self):
        email = str(self.email) or ''
        fail_example = self._get_gravatar_base64('fail@email.gravatar')
        user_gravatar = self._get_gravatar_base64(email)
        if fail_example != user_gravatar:
            self.write({'image': user_gravatar})
        else:
            raise Warning(
                _("You don't have Gravatar image to this %s email." % (
                    email)))
        return True
