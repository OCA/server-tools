# -*- coding: utf-8 -*-
##############################################################################
#
#    (c) Daniel Reis 2015
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class ActionRuleset(models.Model):
    "Rulesets to organize Action Rules"
    _name = 'base.action.ruleset'

    name = fields.Char(required=True)
    model_id = fields.Many2one('ir.model', 'Preferred Model')
    enabled = fields.Boolean('Enabled?')
    silence_errors = fields.Boolean('Silence Errors?')
    runas_user_id = fields.Many2one('res.users', 'User')
    note = fields.Text('Description')
    rule_ids = fields.One2many(
        'base.action.rule',
        'ruleset_id',
        'Action Rules')
    # TODO: Add Ruleset action logs
