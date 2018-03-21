# Copyright (C) 2018-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import hashlib
import urllib
from urllib.error import HTTPError

from odoo import api, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _get_gravatar_url(self):
        """
        Get the gravatar url from the configuration
        :return: str
        """
        config_obj = self.env['ir.config_parameter']
        default_url = "https://www.gravatar.com/avatar/{}?s=200"
        key = "user_gravatar.gravatar_url"
        return config_obj.sudo().get_param(key, default=default_url)

    def _get_gravatar_base64(self, email=''):
        """
        Get the gravatar image encoded in base64
        :param email: str
        :return: base64
        """
        # Unicode-objects must be encoded before hashing
        email = email.encode('utf-8')
        url = self._get_gravatar_url()
        _hash = hashlib.md5(email).hexdigest()
        try:
            res = urllib.request.urlopen(url.format(_hash))
            raw_image = res.read()
            return base64.encodebytes(bytes(raw_image))
        except HTTPError:
            raise UserError(_('Sorry Gravatar not found.'))

    @api.multi
    def get_gravatar_image(self):
        """
        For every users, get the gravatar picture and save it into the image
        field.
        :return: bool
        """
        fail_example = self._get_gravatar_base64('fail@email.gravatar')
        for record in self:
            email = record.email or ''
            user_gravatar = self._get_gravatar_base64(email)
            if fail_example != user_gravatar:
                record.write({'image': user_gravatar})
            else:
                message = _("There is no Gravatar image for this "
                            "email (%s)") % email
                raise UserError(message)
        return True
