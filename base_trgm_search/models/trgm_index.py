# -*- coding: utf-8 -*-
import logging

from openerp import api, exceptions, fields, models
from openerp.osv import expression

from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


class TrgmIndex(models.Model):

    """Model for Trigram Index."""

    _name = 'trgm.index'
    _rec_name = 'field_id'

    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        required=True,
        help='You can either select a field of type "text" or "char".'
    )

    index_name = fields.Char(
        string='Index Name',
        readonly=True,
        help='The index name is automatically generated like '
             'fieldname_indextype_idx. If the index already exists and the '
             'index is located in the same table then this index is resused. '
             'If the index is located in another table then a number is added '
             'at the end of the index name.'
    )

    index_type = fields.Selection(
        selection=[('gin', 'GIN'), ('gist', 'GiST')],
        string='Index Type',
        default='gin',
        required=True,
        help='Cite from PostgreSQL documentation: "As a rule of thumb, a '
             'GIN index is faster to search than a GiST index, but slower to '
             'build or update; so GIN is better suited for static data and '
             'GiST for often-updated data."'
    )

    @api.model
    def _trgm_extension_exists(self):
        self.env.cr.execute("""
            SELECT name, installed_version
            FROM pg_available_extensions
            WHERE name = 'pg_trgm'
            LIMIT 1;
            """)

        extension = self.env.cr.fetchone()
        if extension is None:
            return 'missing'

        if extension[1] is None:
            return 'uninstalled'

        return 'installed'

    @api.model
    def _is_postgres_superuser(self):
        self.env.cr.execute("SHOW is_superuser;")
        superuser = self.env.cr.fetchone()
        return superuser is not None and superuser[0] == 'on' or False

    @api.model
    def _install_trgm_extension(self):
        extension = self._trgm_extension_exists()
        if extension == 'missing':
            _logger.warning('To use pg_trgm you have to install the '
                            'postgres-contrib module.')
        elif extension == 'uninstalled':
            if self._is_postgres_superuser():
                self.env.cr.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                return True
            else:
                _logger.warning('To use pg_trgm you have to create the '
                                'extension pg_trgm in your database or you '
                                'have to be the superuser.')
        else:
            return True
        return False

    @api.model
    def _auto_init(self):
        res = super(TrgmIndex, self)._auto_init()
        self._install_trgm_extension()
        return res

    @api.model
    def get_not_used_index(self, index_name, table_name, inc=1):
        if inc > 1:
            new_index_name = index_name + str(inc)
        else:
            new_index_name = index_name
        self.env.cr.execute("""
            SELECT tablename, indexname
            FROM pg_indexes
            WHERE indexname = %(index)s;
            """, {'index': new_index_name})

        indexes = self.env.cr.fetchone()
        if indexes is not None and indexes[0] == table_name:
            return True, index_name
        elif indexes is not None:
            return self.get_not_used_index(index_name, table_name,
                                           inc + 1)

        return False, new_index_name

    @api.multi
    def create_index(self):
        self.ensure_one()

        if not self._install_trgm_extension():
            raise exceptions.UserError(
                'The pg_trgm extension does not exists or cannot be '
                'installed.')

        table_name = self.env[self.field_id.model_id.model]._table
        column_name = self.field_id.name
        index_type = self.index_type
        index_name = '%s_%s_idx' % (column_name, index_type)
        index_exists, index_name = self.get_not_used_index(
            index_name, table_name)

        if not index_exists:
            self.env.cr.execute("""
            CREATE INDEX %(index)s
            ON %(table)s
            USING %(indextype)s (%(column)s %(indextype)s_trgm_ops);
            """, {
                'table': AsIs(table_name),
                'index': AsIs(index_name),
                'column': AsIs(column_name),
                'indextype': AsIs(index_type)
            })
        return index_name

    @api.model
    def index_exists(self, model_name, field_name):
        field = self.env['ir.model.fields'].search([
            ('model', '=', model_name), ('name', '=', field_name)], limit=1)

        if not field:
            return False

        trgm_index = self.search([('field_id', '=', field.id)], limit=1)
        return bool(trgm_index)

    @api.model
    def create(self, vals):
        rec = super(TrgmIndex, self).create(vals)
        rec.index_name = rec.create_index()
        return rec

    @api.multi
    def unlink(self):
        for rec in self:
            self.env.cr.execute("""
                DROP INDEX IF EXISTS %(index)s;
                """, {
                'index': AsIs(rec.index_name),
            })
        return super(TrgmIndex, self).unlink()


def patch_leaf_trgm(method):
    def decorate_leaf_to_sql(self, eleaf):
        model = eleaf.model
        leaf = eleaf.leaf
        left, operator, right = leaf
        table_alias = '"%s"' % (eleaf.generate_alias())

        if operator == '%':
            sql_operator = '%%'
            params = []

            if left in model._columns:
                format = model._columns[left]._symbol_set[0]
                column = '%s.%s' % (table_alias, expression._quote(left))
                query = '(%s %s %s)' % (column, sql_operator, format)
            elif left in expression.MAGIC_COLUMNS:
                query = "(%s.\"%s\" %s %%s)" % (
                    table_alias, left, sql_operator)
                params = right
            else:  # Must not happen
                raise ValueError(
                    "Invalid field %r in domain term %r" % (left, leaf))

            if left in model._columns:
                params = model._columns[left]._symbol_set[1](right)

            if isinstance(params, basestring):
                params = [params]
            return query, params
        elif operator == 'inselect':
            right = (right[0].replace(' % ', ' %% '), right[1])
            eleaf.leaf = (left, operator, right)
        return method(self, eleaf)
    return decorate_leaf_to_sql
expression.expression._expression__leaf_to_sql = patch_leaf_trgm(
    expression.expression._expression__leaf_to_sql)
expression.TERM_OPERATORS += ('%',)
