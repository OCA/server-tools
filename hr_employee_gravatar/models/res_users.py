# -*- coding: utf-8 -*-
# © 2015 Endika Iglesias
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.one
    def get_gravatar_image(self):
        super(ResUsers, self).get_gravatar_image()
        hr_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.id)])
        hr_employee.write({'image': self.image})
        return True
