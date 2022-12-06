# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, models, fields
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from ..identifier_adapter import IdentifierAdapter


class CleanupPurgeLineField(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.field'
    _description = 'Purge fields'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.field', 'Purge Wizard', readonly=True
    )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        related="field_id.model_id",
        string="Model",
        store=True,
    )
    model_name = fields.Char(
        related="model_id.model",
        string="Model Technical Name",
        store=True,
    )

    @api.multi
    def purge(self):
        """
        Unlink fields upon manual confirmation.
        """
        context_flags = {
            MODULE_UNINSTALL_FLAG: True,
            'purge': True,
        }
        if self:
            objs = self
        else:
            objs = self.env['cleanup.purge.line.action']\
                .browse(self._context.get('active_ids'))
        to_unlink = objs.filtered(lambda x: not x.purged and x.field_id)
        self.logger.info('Purging field entries:')
        for rec in to_unlink:
            self.logger.info(' - %s.%s', rec.model_name, rec.field_id.name)
            field_id = rec.with_context(**context_flags).field_id
            # If store field is not set, the SQL column will not be DROPPED
            # even if exists
            if not field_id.store:
                table_name = self.env[rec.model_name]._table
                column_name = field_id.name
            else:
                table_name = False
                column_name = False
            field_id.unlink()
            if table_name and column_name:
                self._drop_column(table_name, column_name)
            rec.purged = True
        return True

    def _drop_column(self, table, column):
        # Use code from `purge_columns.py::purge()`
        # Check whether the column actually still exists.
        # Inheritance such as stock.picking.in from stock.picking
        # can lead to double attempts at removal
        self.env.cr.execute(
            'SELECT count(attname) FROM pg_attribute '
            'WHERE attrelid = '
            '( SELECT oid FROM pg_class WHERE relname = %s ) '
            'AND attname = %s', (table, column)
        )
        if not self.env.cr.fetchone()[0]:
            return
        self.logger.info('Dropping column %s from table %s', column, table)
        self.env.cr.execute(
            'ALTER TABLE %s DROP COLUMN %s',
            (IdentifierAdapter(table), IdentifierAdapter(column))
        )
        # we need this commit because the ORM will deadlock if
        # we still have a pending transaction
        self.env.cr.commit()  # pylint: disable=invalid-commit


class CleanupPurgeWizardField(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.field'
    _description = 'Purge fields'

    @api.model
    def find(self):
        """
        Search for fields not technically mapped to a model.
        """
        res = []
        ignored_fields = models.MAGIC_COLUMNS + [
            "display_name", models.BaseModel.CONCURRENCY_CHECK_FIELD
        ]
        domain = [('state', '=', 'base')]
        for field_id in self.env['ir.model.fields'].search(domain):
            if field_id.name in ignored_fields:
                continue
            model = self.env[field_id.model_id.model]
            if field_id.name not in model._fields.keys():
                res.append(
                    (0, 0, {
                        'name': field_id.name,
                        'field_id': field_id.id,
                    })
                )
        if not res:
            raise UserError(_('No orphaned fields found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.field', 'wizard_id', 'Fields to purge'
    )
