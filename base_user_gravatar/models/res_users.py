# -*- coding: utf-8 -*-
# © 2015 Endika Iglesias
# © 2017 Hugo Rodrigues
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import hashlib
import urllib2
import logging

from odoo import api, models, fields
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    gravatar_autoupdate = fields.Boolean(
        string='Auto update gravatar'
        )

    gravatar_autoupdate_enabled = fields.Boolean(
        compute='_compute_gravatar_autoupdate_enabled'
        )

    @api.multi
    def _compute_gravatar_autoupdate_enabled(self):
        IrParameter = self.env['ir.config_parameter']
        auto_update = IrParameter.get_param('gravatar.autoupdate')
        for record in self:
            record.gravatar_autoupdate_enabled = auto_update and auto_update.value in ('True', 'true', '1')

    def _get_gravatar_base64(self, email=''):
        url = 'http://www.gravatar.com/avatar/{}?s=200'
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

    @api.model
    def _update_gravatars(self):
        IrParameter = self.env['ir.config_parameter']
        auto_update = IrParameter.get_param('gravatar.autoupdate')
        if auto_update and auto_update.value in ('True', 'true', '1'):
            _logger.info('Starting Gravatar update')
            # Lets prevent failing in case of no gravatar
            for user in self.search([('gravatar_autoupdate', '=', True)]):
                try:
                    user.get_gravatar_image()
                except:
                    _logger.warning('Unable to set Gravatar for email %s' % str(user.email) or '')
            _logger.info('Gravatar auto update ended')
        return True
