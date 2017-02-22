# -*- coding: utf-8 -*-
# Copyright (C) 2015 Akretion (<http://www.akretion.com>)
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import uuid
import StringIO
import base64
from psycopg2 import ProgrammingError

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class SQLRequestMixin(models.Model):
    _name = 'sql.request.mixin'

    _clean_query_enabled = True

    _check_prohibited_words_enabled = True

    _check_execution_enabled = True

    _sql_request_groups_relation = False

    _sql_request_users_relation = False

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sql_valid', 'SQL Valid'),
    ]

    PROHIBITED_WORDS = [
        'delete',
        'drop',
        'insert',
        'alter',
        'truncate',
        'execute',
        'create',
        'update',
        'ir_config_parameter',
    ]

    # Default Section
    @api.model
    def _default_group_ids(self):
        ir_model_obj = self.env['ir.model.data']
        return [ir_model_obj.xmlid_to_res_id(
            'sql_request_abstract.group_sql_request_user')]

    @api.model
    def _default_user_ids(self):
        return []

    # Columns Section
    name = fields.Char('Name', required=True)

    query = fields.Text(
        string='Query', required=True, help="You can't use the following words"
        ": DELETE, DROP, CREATE, INSERT, ALTER, TRUNCATE, EXECUTE, UPDATE")

    state = fields.Selection(
        string='State', selection=STATE_SELECTION, default='draft',
        help="State of the Request:\n"
        " * 'Draft': Not tested\n"
        " * 'SQL Valid': SQL Request has been checked and is valid")

    group_ids = fields.Many2many(
        comodel_name='res.groups', string='Allowed Groups',
        relation=_sql_request_groups_relation,
        column1='sql_id', column2='group_id',
        default=_default_group_ids)

    user_ids = fields.Many2many(
        comodel_name='res.users', string='Allowed Users',
        relation=_sql_request_users_relation,
        column1='sql_id', column2='user_id',
        default=_default_user_ids)

    # Action Section
    @api.multi
    def button_clean_check_request(self):
        for item in self:
            if item._clean_query_enabled:
                item._clean_query()
            if item._check_prohibited_words_enabled:
                item._check_prohibited_words()
            if item._check_execution_enabled:
                item._check_execution()
            item.state = 'sql_valid'

    @api.multi
    def button_set_draft(self):
        self.write({'state': 'draft'})

    # API Section
    @api.multi
    def _execute_sql_request(
            self, params=None, mode='fetchall', rollback=True,
            view_name=False, copy_options="CSV HEADER DELIMITER ';'"):
        """Execute a SQL request on the current database.

        ??? This function checks before if the user has the
        right to execute the request.

        :param params: (dict) of keys / values that will be replaced in
            the sql query, before executing it.
        :param mode: (str) result type expected. Available settings :
            * 'view': create a view with the select query. Extra param
                required 'view_name'.
            * 'materialized_view': create a MATERIALIZED VIEW with the
                select query. Extra parameter required 'view_name'.
            * 'fetchall': execute the select request, and return the
                result of 'cr.fetchall()'.
            * 'fetchone' : execute the select request, and return the
                result of 'cr.fetchone()'
        :param rollback: (boolean) mention if a rollback should be played after
            the execution of the query. Please keep this feature enabled
            for security reason, except if necessary.
            (Ignored if @mode in ('view', 'materialized_view'))
        :param view_name: (str) name of the view.
            (Ignored if @mode not in ('view', 'materialized_view'))
        :param copy_options: (str) mentions extra options for
            "COPY request STDOUT WITH xxx" request.
            (Ignored if @mode != 'stdout')

        ..note:: The following exceptions could be raised:
            psycopg2.ProgrammingError: Error in the SQL Request.
            openerp.exceptions.Warning:
                * 'mode' is not implemented.
                * materialized view is not supported by the Postgresql Server.
        """
        self.ensure_one()
        res = False
        # Check if the request is in a valid state
        if self.state == 'draft':
            raise UserError(_(
                "It is not allowed to execute a not checked request."))

        # Disable rollback if a creation of a view is asked
        if mode in ('view', 'materialized_view'):
            rollback = False

        params = params and params or {}
        query = self.env.cr.mogrify(self.query, params).decode('utf-8')

        if mode in ('fetchone', 'fetchall'):
            pass
        elif mode == 'stdout':
            query = "COPY (%s) TO STDOUT WITH %s" % (query, copy_options)
        elif mode in 'view':
            query = "CREATE VIEW %s AS (%s);" % (query, view_name)
        elif mode in 'materialized_view':
            self._check_materialized_view_available()
            query = "CREATE MATERIALIZED VIEW %s AS (%s);" % (query, view_name)
        else:
            raise UserError(_("Unimplemented mode : '%s'" % mode))

        if rollback:
            rollback_name = self._create_savepoint()
        try:
            if mode == 'stdout':
                output = StringIO.StringIO()
                self.env.cr.copy_expert(query, output)
                output.getvalue()
                res = base64.b64encode(output.getvalue())
                output.close()
            else:
                self.env.cr.execute(query)
                if mode == 'fetchall':
                    res = self.env.cr.fetchall()
                elif mode == 'fetchone':
                    res = self.env.cr.fetchone()
        finally:
            self._rollback_savepoint(rollback_name)

        return res

    # Private Section
    @api.model
    def _create_savepoint(self):
        rollback_name = '%s_%s' % (
            self._name.replace('.', '_'), uuid.uuid1().hex)
        req = "SAVEPOINT %s" % (rollback_name)
        self.env.cr.execute(req)
        return rollback_name

    @api.model
    def _rollback_savepoint(self, rollback_name):
        req = "ROLLBACK TO SAVEPOINT %s" % (rollback_name)
        self.env.cr.execute(req)

    @api.model
    def _check_materialized_view_available(self):
        self.env.cr.execute("SHOW server_version;")
        res = self.env.cr.fetchone()[0].split('.')
        minor_version = float('.'.join(res[:2]))
        return minor_version >= 9.3

    @api.multi
    def _clean_query(self):
        self.ensure_one()
        query = self.query.strip()
        while query[-1] == ';':
            query = query[:-1]
        self.query = query

    @api.multi
    def _check_prohibited_words(self):
        """Check if the query contains prohibited words, to avoid maliscious
        SQL requests"""
        self.ensure_one()
        query = self.query.lower()
        for word in self.PROHIBITED_WORDS:
            expr = r'\b%s\b' % word
            is_not_safe = re.search(expr, query)
            if is_not_safe:
                raise UserError(_(
                    "The query is not allowed because it contains unsafe word"
                    " '%s'") % (word))

    @api.multi
    def _check_execution(self):
        """Ensure that the query is valid, trying to execute it. A rollback
        is done after."""
        self.ensure_one()
        query = self._prepare_request_check_execution()
        rollback_name = self._create_savepoint()
        res = False
        try:
            self.env.cr.execute(query)
            res = self._hook_executed_request()
        except ProgrammingError as e:
            raise UserError(
                _("The SQL query is not valid:\n\n %s") % e.message)
        finally:
            self._rollback_savepoint(rollback_name)
        return res

    @api.multi
    def _prepare_request_check_execution(self):
        """Overload me to replace some part of the query, if it contains
        parameters"""
        self.ensure_one()
        return self.query

    def _hook_executed_request(self):
        """Overload me to insert custom code, when the SQL request has
        been executed, before the rollback.
        """
        self.ensure_one()
        return False
