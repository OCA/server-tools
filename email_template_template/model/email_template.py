# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
from openerp.models.orm import Model
from openerp import fields
from openerp.addons.email_template.email_template import mako_template_env


class email_template(Model):
    _inherit = 'email.template'

    def _get_is_template_template(self, cr, uid, ids, fields_name, arg,
                                  context=None):
        cr.execute('''select
                id, (select count(*) > 0 from email_template e
                    where email_template_id=email_template.id)
                from email_template
                where id in %s''', (tuple(ids),))
        return dict(cr.fetchall())

    _columns = {
        'email_template_id': fields.many2one('email.template', 'Template'),
        'is_template_template': fields.function(
            _get_is_template_template, type='boolean',
            string='Is a template template'),
        }

    def get_email_template(self, cr, uid, template_id=False, record_id=None,
                           context=None):
        this = super(email_template, self).get_email_template(
            cr, uid, template_id, record_id, context)

        if this.email_template_id and not this.is_template_template:
            for field in ['body_html']:
                if this[field] and this.email_template_id[field]:
                    try:
                        mako_template_env.autoescape = False
                        this._data[this.id][field] = self.render_template(
                            cr, uid, this.email_template_id[field],
                            this.email_template_id.model,
                            this.id, this._context)
                    finally:
                        mako_template_env.autoescape = True
        return this
