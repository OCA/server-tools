# -*- coding: utf-8 -*-
#
#    Author: Yannick Vaucher
#    Copyright 2015 Camptocamp SA
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
import logging

from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


class RecordArchiverConfigSettings(orm.TransientModel):
    _name = 'record.archiver.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'lifespan_ids': fields.related(
            'company_id', 'lifespan_ids',
            string='Record Lifespans',
            type='one2many',
            relation='record.lifespan'),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
    }

    def create(self, cr, uid, values, context=None):
        _super = super(RecordArchiverConfigSettings, self)
        rec_id = _super.create(cr, uid, values, context=context)
        # Hack: to avoid some nasty bug, related fields are not written upon
        # record creation.
        # Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [rec_id], vals, context=context)
        return id

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        # update related fields
        if not company_id:
            return {'value': {}}
        company = self.pool.get('res.company'
                                ).browse(cr, uid, company_id, context=context)
        lifespan_ids = [l.id for l in company.lifespan_ids]
        values = {
            'lifespan_ids': lifespan_ids,
        }
        return {'value': values}
