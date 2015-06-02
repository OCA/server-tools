# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Buron. Copyright Yannick Buron
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tests.common import TransactionCase


class BaseConfigInheritTestModel(orm.Model):

    """
    Abstract class used by project and task to create config lines.
    Inherit base.config.inherit.model.
    """

    _name = 'base.config.inherit.test.model'
    _inherit = ['base.config.inherit.model', 'base.recursive.model']

    _base_config_inherit_model = 'base.config.inherit.test.line'
    _base_config_inherit_key = 'test_field'
    _base_config_inherit_o2m = 'test_config_ids'

    _columns = {
        'name': fields.char('Name', size=64),
        'parent_id': fields.many2one('base.config.inherit.test.model',
                                     'Parent', ondelete='restrict'),
        'test_config_ids': fields.one2many(
            'base.config.inherit.test.line', 'res_id',
            domain=lambda self: [
                ('model', '=', self._name), ('stored', '=', False)
            ],
            auto_join=True,
            string='Test Config'
        ),
        'test_config_result_ids': fields.one2many(
            'base.config.inherit.test.line', 'res_id',
            domain=lambda self: [
                ('model', '=', self._name), ('stored', '=', True)
            ],
            auto_join=True,
            string='Test Config Result', readonly=True
        ),
        'sequence': fields.integer('Sequence')
    }

    def _prepare_config(self, cr, uid, id, record, vals=None, context=None):
        # Specify the fields contained in the configuration

        if vals is None:
            vals = {}

        res = {
            'model': self._name,
            'res_id': id,
            'test_field': 'test_field' in record
                          and record.test_field.id or False,
            'sequence': 'sequence' in record
                        and record.sequence or False,
            'stored': True
        }

        res.update(super(BaseConfigInheritTestModel, self)._prepare_config(
            cr, uid, id, record, vals=vals, context=context
        ))
        return res

    def get_config(self, cr, uid, id, context=None):
        res = []
        for line in self.browse(cr, uid, id, context=context)\
                .test_config_result_ids:
            res.append(line.test_field.name)
        return res


class BaseConfigInheritTestLine(orm.Model):

    _name = 'base.config.inherit.test.line'
    _inherit = 'base.config.inherit.line'

    _columns = {
        'test_field': fields.many2one('base.config.inherit.test.model', 'Test')
    }


class TestBaseConfigInherit(TransactionCase):

    def test_run(self):

        test_model = self.env['base.config.inherit.test.model']
        record1 = test_model.create(
            {'name': 'Record1'})
        record2 = test_model.create(
            {'name': 'Record2',
             'parent_id': record1.id})
        record1.write({'test_config_ids': [(0, 0, {
            'model': 'base.config.inherit.test.model',
            'sequence': 5,
            'test_field': record1.id
        })]})
        self.assertEqual(record2.get_config(), [['Record1']])
