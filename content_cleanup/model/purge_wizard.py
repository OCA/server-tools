# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2016 Clear ICT Solutions (<info@clearict.com>).
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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

import logging
import psycopg2
from openerp import api, exceptions, fields, models, workflow
from openerp.tools.translate import _


class PurgeWizardLineExtraTables(models.TransientModel):
    """ Additional database tables whose content should be removed """

    _name = 'cleanup.content.wizard.line.extra.tables'

    # Fields
    wizard_line = fields.Many2one('cleanup.content.wizard.line',
                                  'Wizard line', readonly=True)
    name = fields.Char(readonly=True)


class PurgeWizardLine(models.TransientModel):
    """ Invidual lines representing models to cleanup """

    _name = 'cleanup.content.wizard.line'

    # Fields
    #
    wizard = fields.Many2one('cleanup.content.wizard',
                             'Content cleanup wizard', readonly=True)
    name = fields.Char(readonly=True, string='Table')
    model_name = fields.Char(readonly=True)
    purged = fields.Boolean(readonly=True)
    extra_tables = fields.One2many('cleanup.content.wizard.line.extra.tables',
                                   'wizard_line', string="Additonal tables")

    logger = logging.getLogger('openerp.addons.content_cleanup')

    @api.multi
    def purge(self):
        """
        Delete all data in this table and all other tables with foreign-key
        constraints (if selected) on it. Also, restarts sequences owned by
        columns in the table.
        """

        purged_lines = []
        for line in self:
            if line.purged:
                continue

            self._line_purge_properties(line)
            self._line_purge_model_data(line)
            self._line_purge_ir_values(line)
            self._line_purge_attachments(line)
            self._line_purge_workflows(line)

            purged_lines.append(line)

        table_names = ''
        for pl in purged_lines:
            if len(table_names) != 0:
                table_names = table_names + ',' + pl.name
            else:
                table_names += pl.name
            for tbl in pl.extra_tables:
                table_names = table_names + ',' + tbl.name

        strCascade = """"""
        if self[0].wizard.cascade:
            strCascade = """CASCADE"""

        self.logger.info(
            _('Truncating table(s): %s.' % table_names))
        try:
            self.env.cr.execute(
                """
                TRUNCATE TABLE %s
                RESTART IDENTITY %s;
                """ % (table_names, strCascade))
        except psycopg2.NotSupportedError as ex:
            if ex.pgcode == psycopg2.errorcodes.FEATURE_NOT_SUPPORTED:
                raise exceptions.Warning(
                    "Unable to truncate table",
                    "%s" % ex
                )
            else:
                raise
        else:
            # This is OK because the only records we didn't process are the
            # ones where 'purged' == True
            self.write({'purged': True})

        return

    @api.model
    def _line_purge_properties(self, line):
        """
        Delete properties records referencing model in line to be purged.
        """

        domain = [('res_id', 'like', '%s,%%' % line.model_name)]
        return self._line_purge_references_common(
            line.model_name, 'ir.property', domain
        )

    @api.model
    def _line_purge_model_data(self, line):
        """
        Delete ir.model.data records referencing model in line to be purged.
        """

        domain = [('model', '=', line.model_name)]
        return self._line_purge_references_common(
            line.model_name, 'ir.model.data', domain
        )

    @api.model
    def _line_purge_ir_values(self, line):
        """
        Delete ir.values records referencing model in line to be purged.
        """

        domain = [('model', '=', line.model_name)]
        return self._line_purge_references_common(
            line.model_name, 'ir.values', domain
        )

    @api.model
    def _line_purge_attachments(self, line):
        """
        Delete ir.attachment records referencing model in line to be purged.
        """

        # Comment in openerp/models.py unlink() says attachment obj search()
        # method doesn't return attachments of deleted objects. Use SQL as
        # workaround.
        self.env.cr.execute(
            """
            SELECT id
            FROM ir_attachment
            WHERE res_model = '%s'
            """ % (line.model_name,)
        )
        attach_ids = [data[0] for data in self.env.cr.fetchall()]
        return self._line_purge_references_common(
            line.model_name, 'ir.attachment', None, unlink_ids=attach_ids
        )

    @api.model
    def _line_purge_workflows(self, line):
        """
        Delete workflow items of model in line to be purged.
        """

        # Use shortcut to obtain all records in model with a workflow in
        # progress directly from the workflow work-item table. Then, delete
        # the workflow using normal workflow method.
        self.env.cr.execute(
            """
            SELECT res_id
            FROM wkf_instance
            WHERE res_type = '%s'
            """ % (line.model_name,)
        )
        model_ids = [data[0] for data in self.env.cr.fetchall()]
        for res_id in model_ids:
            workflow.trg_delete(
                self.env.uid, line.model_name, res_id, self.env.cr
            )
        self.logger.info(
            _('Removed %s workflows in progress referencing model %s')
            % (len(model_ids), line.model_name))

        return

    @api.model
    def _line_purge_references_common(self, line_model_name, model_name,
                                      domain, unlink_ids=None):
        """
        Base method for removing records from tables referencing model of
        content to be purged.
        """

        obj = self.env[model_name]
        if unlink_ids is None:
            obj_ids = obj.search(domain)
        else:
            obj_ids = obj.search([('id', 'in', unlink_ids)])
        obj_ids.unlink()
        self.logger.info(
            _('Removed %s %s records referencing model %s')
            % (len(obj_ids), model_name, line_model_name))

        return


class PurgeWizard(models.TransientModel):
    """ Main wizard for cleaning up model content """

    _name = 'cleanup.content.wizard'

    @api.model
    def default_get(self, fields):

        res = super(PurgeWizard, self).default_get(fields)
        if 'purge_lines' in fields:
            res['purge_lines'] = self.find()
        return res

    @api.model
    def get_model_list(self):
        """
        Returns a list of models whose content should be removed.
        """

        return []

    @api.model
    def get_extra_tables_list(self):
        """
        Returns a list of dictionaries containing additional database table
        names to reset for each model:
            { 'model.name': ['extra_table1', 'extra_table2'] }
        """

        return []

    @api.model
    def get_extra_tables_by_model(self, model_name):

        res = []
        for data in self.get_extra_tables_list():
            for k, v in data.items():
                if k == model_name:
                    res = v
                    return res
        return res

    @api.model
    def find(self):
        """
        Returns a dictionary containing records of wizard lines to
        create.
        """

        uniq_model_list = list(set([mdl for mdl in self.get_model_list()]))
        res = [
            (0, 0, {
                'name': self.env[mdl]._table,
                'model_name': mdl,
                'extra_tables': [
                    (0, 0, {'name': tbl_name})
                    for tbl_name in self.get_extra_tables_by_model(mdl)
                ]
            })
            for mdl in uniq_model_list
        ]

        return res

    @api.multi
    def purge_all(self):
        for wizard in self:
            wizard.purge_lines.purge()
        return

    # Fields
    #
    name = fields.Char(readonly=True)
    cascade = fields.Boolean(
        default=False,
        help="Remove content from tables with foreign-key references to "
             "tables to be purged.")
    purge_lines = fields.One2many(
        'cleanup.content.wizard.line', 'wizard',
        string='Model content to cleanup')
