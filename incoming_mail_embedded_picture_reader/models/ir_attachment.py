# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def _get_image_url(self):
        """
        :rtype: String or False
        :rparam: URL to access attachment data if a base_url is found
        """
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if base_url:
            return '%s/web/binary/image?model=%s&field=datas&id=%s' % (
                base_url, self._name, self.id)
        return False
