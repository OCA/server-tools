# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
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
#

import re
import psycopg2
from openerp.osv import orm, fields
from openerp.tools.translate import _

# views are created with a prefix to prevent conflicts
SQL_VIEW_PREFIX = u'sql_view_'
# 63 chars is the length of a postgres identifier
USER_NAME_SIZE = 63 - len(SQL_VIEW_PREFIX)

PG_NAME_RE = re.compile(r'^[a-z_][a-z0-9_$]*$', re.I)


class SQLView(orm.Model):
    _name = 'sql.view'
    _description = 'SQL Views'

    def _complete_from_sql_name(self, cr, uid, sql_name, context=None):
        return SQL_VIEW_PREFIX + (sql_name or '')

    def _compute_complete_sql_name(self, cr, uid, ids, name, args,
                                   context=None):
        res = {}
        for sql_view in self.browse(cr, uid, ids, context=context):
            res[sql_view.id] = self._complete_from_sql_name(cr, uid,
                                                            sql_view.sql_name,
                                                            context=context)
        return res

    _columns = {
        'name': fields.char(string='View Name', required=True),
        'sql_name': fields.char(string='SQL Name', required=True,
                                size=USER_NAME_SIZE,
                                help="Name of the view. Will be prefixed "
                                     "by %s" % (SQL_VIEW_PREFIX,)),
        'complete_sql_name': fields.function(_compute_complete_sql_name,
                                             string='Complete SQL Name',
                                             readonly=True,
                                             type='char'),
        'definition': fields.text(string='Definition', required=True),
    }

    def _check_sql_name(self, cr, uid, ids, context=None):
        records = self.browse(cr, uid, ids, context=context)
        return all(PG_NAME_RE.match(record.sql_name) for record in records)

    def _check_definition(self, cr, uid, ids, context=None):
        """ Forbid a SQL definition with unbalanced parenthesis.

        The reason is that the view's definition will be enclosed in:

            CREATE VIEW {view_name} AS ({definition})

        The parenthesis around the definition prevent users to inject
        and execute arbitrary queries after the SELECT part (by using a
        semicolon).  However, it would still be possible to craft a
        definition like the following which would close the parenthesis
        and start a new query:

            SELECT * FROM res_users); DELETE FROM res_users WHERE id IN (1

        This is no longer possible if we ensure that we don't have an
        unbalanced closing parenthesis.

        """
        for record in self.browse(cr, uid, ids, context=context):
            balanced = 0
            for char in record.definition:
                if char == '(':
                    balanced += 1
                elif char == ')':
                    balanced -= 1
                if balanced == -1:
                    return False
        return True

    _constraints = [
        (_check_sql_name,
         'The SQL name is not a valid PostgreSQL identifier',
         ['sql_name']),
        (_check_definition,
         'This SQL definition is not allowed',
         ['definition']),
    ]

    _sql_constraints = [
        ('sql_name_uniq', 'unique (sql_name)',
         'Another view has the same SQL name.')
    ]

    def _sql_view_comment(self, cr, uid, sql_view, context=None):
        return "%s (created by the module sql_view)" % sql_view.name

    def _create_or_replace_sql_view(self, cr, uid, sql_view, context=None):
        view_name = sql_view.complete_sql_name
        try:
            # The parenthesis around the definition are important:
            # they prevent to insert a semicolon and another query after
            # the view declaration
            cr.execute(
                "CREATE VIEW {view_name} AS ({definition})".format(
                    view_name=view_name,
                    definition=sql_view.definition)
            )
        except psycopg2.ProgrammingError as err:
            raise orm.except_orm(
                _('Error'),
                _('The definition of the view is not correct:\n\n%s') % (err,)
            )
        comment = self._sql_view_comment(cr, uid, sql_view, context=context)
        cr.execute(
            "COMMENT ON VIEW {view_name} IS %s".format(view_name=view_name),
            (comment,)
        )

    def _delete_sql_view(self, cr, uid, sql_view, context=None):
        view_name = sql_view.complete_sql_name
        cr.execute("DROP view IF EXISTS %s" % (view_name,))

    def create(self, cr, uid, vals, context=None):
        record_id = super(SQLView, self).create(cr, uid, vals,
                                                context=context)

        record = self.browse(cr, uid, record_id, context=context)
        self._create_or_replace_sql_view(cr, uid, record, context=context)
        return record_id

    def write(self, cr, uid, ids, vals, context=None):
        # If the name has been changed, we have to drop the view,
        # it will be created with the new name.
        # If the definition have been changed, we better have to delete
        # it and create it again otherwise we can have 'cannot drop
        # columns from view' errors.
        for record in self.browse(cr, uid, ids, context=context):
            self._delete_sql_view(cr, uid, record, context=context)

        result = super(SQLView, self).write(cr, uid, ids, vals,
                                            context=context)
        for record in self.browse(cr, uid, ids, context=context):
            self._create_or_replace_sql_view(cr, uid, record,
                                             context=context)
        return result

    def unlink(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self._delete_sql_view(cr, uid, record, context=context)
        result = super(SQLView, self).unlink(cr, uid, ids, context=context)
        return result

    def onchange_sql_name(self, cr, uid, ids, sql_name, context=None):
        complete_name = self._complete_from_sql_name(cr, uid, sql_name,
                                                     context=context)
        return {'value': {'complete_sql_name': complete_name}}
