# Copyright 2015-2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)


class RecordLifespan(models.Model):
    """Configure records lifespans per model.

    After the lifespan is expired (compared to the `write_date` of the
    records), the records are deactivated.
    """
    _name = 'record.lifespan'
    _order = 'model_name'

    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        domain=[('has_an_active_field', '=', True)],
    )
    model_name = fields.Char(
        related='model_id.model',
        readonly=True,
        string='Model Name',
    )
    months = fields.Integer(
        required=True,
        help="Number of month after which the records will be set to inactive"
        " based on their write date",
    )
    archive_states = fields.Char(
        help="Comma-separated list of states in which records should be"
        " archived. Implicit value is `'done, cancel')`.",
    )

    _sql_constraints = [
        ('months_gt_0', 'check (months > 0)',
         "Months must be a value greater than 0"),
    ]

    @api.constrains('archive_states')
    def _check_archive_states(self):
        for lifespan in self:
            if not lifespan.archive_states:
                continue
            model = self.env[lifespan.model_id.model]
            state_field = model.fields_get().get('state', {})
            if not state_field:
                continue
            allowed_states \
                = [x[0] for x in state_field.get('selection', [('')])]
            if not all(archive_state in allowed_states
                       for archive_state in lifespan._get_archive_states()):
                raise exceptions.ValidationError(_(
                    'Invalid set of states for "%s" model:\n'
                    '%s\n'
                    'Valid states:\n%s'
                ) % (
                    lifespan.model_id.name,
                    lifespan.archive_states,
                    '\n'.join('- {}'.format(s) for s in allowed_states),
                ))

    @api.model
    def _scheduler_archive_records(self):
        lifespans = self.search([])
        _logger.info('Records archiver starts archiving records')
        for lifespan in lifespans:
            try:
                lifespan.archive_records()
            except exceptions.UserError as e:
                _logger.error("Archiver error:\n%s", e[1])
        _logger.info('Rusty Records now rest in peace')
        return True

    @api.multi
    def _get_archive_states(self):
        self.ensure_one()
        if not self.archive_states:
            return ['done', 'cancel']
        return [s.strip() for s in self.archive_states.split(',')]

    @api.multi
    def _archive_domain(self, expiration_date):
        """Returns the domain used to find the records to archive.

        Can be inherited to change the archived records for a model.
        """
        self.ensure_one()
        model = self.env[self.model_id.model]
        domain = [('write_date', '<', expiration_date)]
        if 'state' in model.fields_get_keys():
            domain += [('state', 'in', self._get_archive_states())]
        return domain

    @api.multi
    def _archive_lifespan_records(self):
        """Archive the records for a lifespan, so for a model.

        Can be inherited to customize the archive strategy.
        The default strategy is to change the field ``active`` to False
        on the records having a ``write_date`` older than the lifespan.
        Only done and canceled records will be deactivated.

        """
        self.ensure_one()
        today = datetime.today()
        model_name = self.model_id.model
        model = self.env[model_name]
        if not isinstance(model, models.Model):
            raise exceptions.UserError(
                _('Model %s not found') % model_name)
        if 'active' not in model.fields_get_keys():
            raise exceptions.UserError(
                _('Model %s has no active field') % model_name)

        delta = relativedelta(months=self.months)
        expiration_date = fields.Datetime.to_string(today - delta)

        domain = self._archive_domain(expiration_date)
        recs = model.search(domain)
        if not recs:
            return

        recs.with_context(tracking_disable=True).toggle_active()
        _logger.info(
            'Archived %s %s older than %s',
            len(recs.ids), model_name, expiration_date)

    @api.multi
    def archive_records(self):
        """Call the archiver for several record lifespans."""
        for lifespan in self:
            lifespan._archive_lifespan_records()
        return True
