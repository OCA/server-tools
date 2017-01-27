# -*- coding: utf-8 -*-
# Copyright 2015-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby
from lxml import etree
from operator import attrgetter

from odoo import models, fields, api, exceptions, _
from odoo.osv.orm import setup_modifiers

# sentinel object to be sure that no empty value was passed to
# ResPartnerChangesetChange._value_for_changeset
_NO_VALUE = object()


class ResPartnerChangeset(models.Model):
    _name = 'res.partner.changeset'
    _description = 'Partner Changeset'
    _order = 'date desc'
    _rec_name = 'date'

    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string='Partner',
                                 index=True,
                                 required=True,
                                 readonly=True,
                                 ondelete='cascade')
    change_ids = fields.One2many(comodel_name='res.partner.changeset.change',
                                 inverse_name='changeset_id',
                                 string='Changes',
                                 readonly=True)
    date = fields.Datetime(default=fields.Datetime.now,
                           index=True,
                           readonly=True)
    state = fields.Selection(
        compute='_compute_state',
        selection=[('draft', 'Pending'),
                   ('done', 'Done')],
        string='State',
        store=True,
    )
    note = fields.Text()
    source = fields.Reference(
        string='Source of the change',
        selection='_reference_models',
        readonly=True,
    )

    @api.model
    def _reference_models(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    @api.one
    @api.depends('change_ids', 'change_ids.state')
    def _compute_state(self):
        if all(change.state in ('done', 'cancel') for change
                in self.mapped('change_ids')):
            self.state = 'done'
        else:
            self.state = 'draft'

    @api.multi
    def apply(self):
        self.mapped('change_ids').apply()

    @api.multi
    def cancel(self):
        self.mapped('change_ids').cancel()

    @api.multi
    def add_changeset(self, record, values):
        """ Add a changeset on a partner

        By default, when a partner is modified by a user or by the
        system, the the changeset will follow the rules configured for
        the 'Users' / global rules.

        A caller should pass the following keys in the context:

        * ``__changeset_rules_source_model``: name of the model which
          asks for the change
        * ``__changeset_rules_source_id``: id of the record which asks
        for the change

        When the source model and id are not defined, the current user
        is considered as the origin of the change.

        Should be called before the execution of ``write`` on the record
        so we can keep track of the existing value and also because the
        returned values should be used for ``write`` as some of the
        values may have been removed.

        :param values: the values being written on the partner
        :type values: dict

        :returns: dict of values that should be wrote on the partner
        (fields with a 'Validate' or 'Never' rule are excluded)

        """
        record.ensure_one()

        source_model = self.env.context.get('__changeset_rules_source_model')
        source_id = self.env.context.get('__changeset_rules_source_id')
        if not source_model:
            # if the changes source is not defined, log the user who
            # made the change
            source_model = 'res.users'
        if not source_id:
            source_id = self.env.uid
        if source_model and source_id:
            source = '%s,%s' % (source_model, source_id)
        else:
            source = False

        change_model = self.env['res.partner.changeset.change']
        write_values = values.copy()
        changes = []
        rules = self.env['changeset.field.rule'].get_rules(
            source_model_name=source_model,
        )
        for field in values:
            rule = rules.get(field)
            if not rule:
                continue
            if field in values:
                if not change_model._has_field_changed(record, field,
                                                       values[field]):
                    continue
            change, pop_value = change_model._prepare_changeset_change(
                record, rule, field, values[field]
            )
            if pop_value:
                write_values.pop(field)
            changes.append(change)
        if changes:
            self.env['res.partner.changeset'].create({
                'partner_id': record.id,
                'change_ids': [(0, 0, vals) for vals in changes],
                'date': fields.Datetime.now(),
                'source': source,
            })
        return write_values


class ResPartnerChangesetChange(models.Model):
    """ Store the change of one field for one changeset on one partner

    This model is composed of 3 sets of fields:

    * 'origin'
    * 'old'
    * 'new'

    The 'new' fields contain the value that needs to be validated.
    The 'old' field copies the actual value of the partner when the
    change is either applied either canceled. This field is used as a storage
    place but never shown by itself.
    The 'origin' fields is a related field towards the actual values of
    the partner until the change is either applied either canceled, past
    that it shows the 'old' value.
    The reason behind this is that the values may change on a partner between
    the moment when the changeset is created and when it is applied.

    On the views, we show the origin fields which represent the actual
    partner values or the old values and we show the new fields.

    The 'origin' and 'new_value_display' are displayed on
    the tree view where we need a unique of field, the other fields are
    displayed on the form view so we benefit from their widgets.

    """
    _name = 'res.partner.changeset.change'
    _description = 'Partner Changeset Change'
    _rec_name = 'field_id'

    changeset_id = fields.Many2one(comodel_name='res.partner.changeset',
                                   required=True,
                                   string='Changeset',
                                   ondelete='cascade',
                                   readonly=True)
    field_id = fields.Many2one(comodel_name='ir.model.fields',
                               string='Field',
                               required=True,
                               readonly=True)
    field_type = fields.Selection(related='field_id.ttype',
                                  string='Field Type',
                                  readonly=True)

    origin_value_display = fields.Char(
        string='Previous',
        compute='_compute_value_display',
    )
    new_value_display = fields.Char(
        string='New',
        compute='_compute_value_display',
    )

    # Fields showing the origin partner's value or the 'old' value if
    # the change is applied or canceled.
    origin_value_char = fields.Char(compute='_compute_origin_values',
                                    string='Previous',
                                    readonly=True)
    origin_value_date = fields.Date(compute='_compute_origin_values',
                                    string='Previous',
                                    readonly=True)
    origin_value_datetime = fields.Datetime(compute='_compute_origin_values',
                                            string='Previous',
                                            readonly=True)
    origin_value_float = fields.Float(compute='_compute_origin_values',
                                      string='Previous',
                                      readonly=True)
    origin_value_integer = fields.Integer(compute='_compute_origin_values',
                                          string='Previous',
                                          readonly=True)
    origin_value_text = fields.Text(compute='_compute_origin_values',
                                    string='Previous',
                                    readonly=True)
    origin_value_boolean = fields.Boolean(compute='_compute_origin_values',
                                          string='Previous',
                                          readonly=True)
    origin_value_reference = fields.Reference(
        compute='_compute_origin_values',
        string='Previous',
        selection='_reference_models',
        readonly=True,
    )

    # Fields storing the previous partner's values (saved when the
    # changeset is applied)
    old_value_char = fields.Char(string='Old',
                                 readonly=True)
    old_value_date = fields.Date(string='Old',
                                 readonly=True)
    old_value_datetime = fields.Datetime(string='Old',
                                         readonly=True)
    old_value_float = fields.Float(string='Old',
                                   readonly=True)
    old_value_integer = fields.Integer(string='Old',
                                       readonly=True)
    old_value_text = fields.Text(string='Old',
                                 readonly=True)
    old_value_boolean = fields.Boolean(string='Old',
                                       readonly=True)
    old_value_reference = fields.Reference(string='Old',
                                           selection='_reference_models',
                                           readonly=True)

    # Fields storing the value applied on the partner
    new_value_char = fields.Char(string='New',
                                 readonly=True)
    new_value_date = fields.Date(string='New',
                                 readonly=True)
    new_value_datetime = fields.Datetime(string='New',
                                         readonly=True)
    new_value_float = fields.Float(string='New',
                                   readonly=True)
    new_value_integer = fields.Integer(string='New',
                                       readonly=True)
    new_value_text = fields.Text(string='New',
                                 readonly=True)
    new_value_boolean = fields.Boolean(string='New',
                                       readonly=True)
    new_value_reference = fields.Reference(string='New',
                                           selection='_reference_models',
                                           readonly=True)

    state = fields.Selection(
        selection=[('draft', 'Pending'),
                   ('done', 'Accepted'),
                   ('cancel', 'Rejected'),
                   ],
        required=True,
        default='draft',
        readonly=True,
    )

    @api.model
    def _reference_models(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    _suffix_to_types = {
        'char': ('char', 'selection'),
        'date': ('date',),
        'datetime': ('datetime',),
        'float': ('float',),
        'integer': ('integer',),
        'text': ('text',),
        'boolean': ('boolean',),
        'reference': ('many2one',),
    }

    _type_to_suffix = {ftype: suffix
                       for suffix, ftypes in _suffix_to_types.iteritems()
                       for ftype in ftypes}

    _origin_value_fields = ['origin_value_%s' % suffix
                            for suffix in _suffix_to_types]
    _old_value_fields = ['old_value_%s' % suffix
                         for suffix in _suffix_to_types]
    _new_value_fields = ['new_value_%s' % suffix
                         for suffix in _suffix_to_types]
    _value_fields = (_origin_value_fields +
                     _old_value_fields +
                     _new_value_fields)

    @api.one
    @api.depends('changeset_id.partner_id')
    def _compute_origin_values(self):
        field_name = self.get_field_for_type(self.field_id, 'origin')
        if self.state == 'draft':
            value = self.changeset_id.partner_id[self.field_id.name]
        else:
            old_field = self.get_field_for_type(self.field_id, 'old')
            value = self[old_field]
        setattr(self, field_name, value)

    @api.one
    @api.depends(lambda self: self._value_fields)
    def _compute_value_display(self):
        for prefix in ('origin', 'new'):
            value = getattr(self, 'get_%s_value' % prefix)()
            if self.field_id.ttype == 'many2one' and value:
                value = value.display_name
            setattr(self, '%s_value_display' % prefix, value)

    @api.model
    def get_field_for_type(self, field, prefix):
        assert prefix in ('origin', 'old', 'new')
        field_type = self._type_to_suffix.get(field.ttype)
        if not field_type:
            raise NotImplementedError(
                'field type %s is not supported' % field_type
            )
        return '%s_value_%s' % (prefix, field_type)

    @api.multi
    def get_origin_value(self):
        self.ensure_one()
        field_name = self.get_field_for_type(self.field_id, 'origin')
        return self[field_name]

    @api.multi
    def get_new_value(self):
        self.ensure_one()
        field_name = self.get_field_for_type(self.field_id, 'new')
        return self[field_name]

    @api.multi
    def set_old_value(self):
        """ Copy the value of the partner to the 'old' field """
        for change in self:
            # copy the existing partner's value for the history
            old_value_for_write = self._value_for_changeset(
                change.changeset_id.partner_id,
                change.field_id.name
            )
            old_field_name = self.get_field_for_type(change.field_id, 'old')
            change.write({old_field_name: old_value_for_write})

    @api.multi
    def apply(self):
        """ Apply the change on the changeset's partner

        It is optimized thus that it makes only one write on the partner
        per changeset if many changes are applied at once.
        """
        changes_ok = self.browse()
        key = attrgetter('changeset_id')
        for changeset, changes in groupby(self.sorted(key=key), key=key):
            values = {}
            partner = changeset.partner_id
            for change in changes:
                if change.state in ('cancel', 'done'):
                    continue

                field = change.field_id
                value_for_write = change._convert_value_for_write(
                    change.get_new_value(),
                    partner
                )
                values[field.name] = value_for_write

                change.set_old_value()

                changes_ok |= change

            if not values:
                continue

            previous_changesets = self.env['res.partner.changeset'].search(
                [('date', '<', changeset.date),
                 ('state', '=', 'draft'),
                 ('partner_id', '=', changeset.partner_id.id),
                 ],
                limit=1,
            )
            if previous_changesets:
                raise exceptions.Warning(
                    _('This change cannot be applied because a previous '
                      'changeset for the same partner is pending.\n'
                      'Apply all the anterior changesets before applying '
                      'this one.')
                )

            partner.with_context(__no_changeset=True).write(values)

        changes_ok.write({'state': 'done'})

    @api.multi
    def cancel(self):
        """ Reject the change """
        if any(change.state == 'done' for change in self):
            raise exceptions.Warning(
                _('This change has already be applied.')
            )
        self.set_old_value()
        self.write({'state': 'cancel'})

    @api.model
    def _has_field_changed(self, record, field, value):
        field_def = record._fields[field]
        current_value = field_def.convert_to_write(record[field], record)
        if not (current_value or value):
            return False
        return current_value != value

    @api.multi
    def _convert_value_for_write(self, value, record):
        if not value:
            return value
        model = self.env[self.field_id.model_id.model]
        model_field_def = model._fields[self.field_id.name]
        return model_field_def.convert_to_write(value, record)

    @api.model
    def _value_for_changeset(self, record, field_name, value=_NO_VALUE):
        """ Return a value from the record ready to write in a changeset field

        :param record: modified record
        :param field_name: name of the modified field
        :param value: if no value is given, it is read from the record
        """
        field_def = record._fields[field_name]
        if value is _NO_VALUE:
            # when the value is read from the record, we need to prepare
            # it for the write (e.g. extract .id from a many2one record)
            value = field_def.convert_to_write(record[field_name], record)
        if field_def.type == 'many2one':
            # store as 'reference'
            comodel = field_def.comodel_name
            return "%s,%s" % (comodel, value) if value else False
        else:
            return value

    @api.multi
    def _prepare_changeset_change(self, record, rule, field_name, value):
        """ Prepare data for a changeset change

        It returns a dict of the values to write on the changeset change
        and a boolean that indicates if the value should be popped out
        of the values to write on the model.

        :returns: dict of values, boolean
        """
        new_field_name = self.get_field_for_type(rule.field_id, 'new')
        new_value = self._value_for_changeset(record, field_name, value=value)
        change = {
            new_field_name: new_value,
            'field_id': rule.field_id.id,
        }
        if rule.action == 'auto':
            change['state'] = 'done'
            pop_value = False
        elif rule.action == 'validate':
            change['state'] = 'draft'
            pop_value = True  # change to apply manually
        elif rule.action == 'never':
            change['state'] = 'cancel'
            pop_value = True  # change never applied

        if change['state'] in ('cancel', 'done'):
            # Normally the 'old' value is set when we use the 'apply'
            # button, but since we short circuit the 'apply', we
            # directly set the 'old' value here
            old_field_name = self.get_field_for_type(rule.field_id, 'old')
            # get values ready to write as expected by the changeset
            # (for instance, a many2one is written in a reference
            # field)
            origin_value = self._value_for_changeset(record, field_name)
            change[old_field_name] = origin_value

        return change, pop_value

    def fields_view_get(self, *args, **kwargs):
        _super = super(ResPartnerChangesetChange, self)
        result = _super.fields_view_get(*args, **kwargs)
        if result['type'] != 'form':
            return
        doc = etree.XML(result['arch'])
        for suffix, ftypes in self._suffix_to_types.iteritems():
            for prefix in ('origin', 'old', 'new'):
                field_name = '%s_value_%s' % (prefix, suffix)
                field_nodes = doc.xpath("//field[@name='%s']" % field_name)
                for node in field_nodes:
                    node.set(
                        'attrs',
                        "{'invisible': "
                        "[('field_type', 'not in', %s)]}" % (ftypes,)
                    )
                    setup_modifiers(node)
        result['arch'] = etree.tostring(doc)
        return result
