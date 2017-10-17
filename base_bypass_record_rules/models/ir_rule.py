# -*- coding: utf-8 -*-
# © 2017 innoviù Srl <http://www.innoviu.com>
# © 2017 Agile Business Group Sagl <http://www.agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class IrRule(models.Model):
    _inherit = 'ir.rule'

    can_be_bypassed = fields.Boolean("Can be bypassed")

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(IrRule, self).read(fields=fields, load=load)
        # result variable has this shape:
        #  [
        #      {
        #          'id': 1,
        #          'domain': [('a', '=', 'b')]
        #      }
        #  ]
        groups_names = self._context.get('can_bypass_record_rules')
        for rule in self:
            if rule.can_be_bypassed and \
                    self.check_groups_for_bypass(self.env.user, groups_names):
                # Assign an 'always True' domain
                # to the dictionary having id == rule.id
                for read_rule in result:
                    if read_rule['id'] == rule.id and 'domain' in read_rule:
                        read_rule['domain'] = [(1, '=', 1)]
        return result

    @staticmethod
    def check_groups_for_bypass(user, groups_names):
        if not groups_names:
            groups_names = []
        return any([user.has_group(group_name)
                    for group_name in groups_names])
