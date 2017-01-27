# -*- coding: utf-8 -*-
# Copyright 2015-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.cache import ormcache


class ChangesetFieldRule(models.Model):
    _name = 'changeset.field.rule'
    _description = 'Changeset Field Rules'
    _rec_name = 'field_id'

    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        domain="[('model_id.model', '=', 'res.partner'), "
               " ('ttype', 'in', ('char', 'selection', 'date', 'datetime', "
               "                 'float', 'integer', 'text', 'boolean', "
               "                 'many2one')), "
               " ('readonly', '=', False)]",
        ondelete='cascade',
        required=True,
    )
    action = fields.Selection(
        selection='_selection_action',
        string='Action',
        required=True,
        help="Auto: always apply a change.\n"
             "Validate: manually applied by an administrator.\n"
             "Never: change never applied.",
    )
    source_model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Source Model',
        ondelete='cascade',
        domain=lambda self: [('id', 'in', self._domain_source_models().ids)],
        help="If a source model is defined, the rule will be applied only "
             "when the change is made from this origin.  "
             "Rules without source model are global and applies to all "
             "backends.\n"
             "Rules with a source model have precedence over global rules, "
             "but if a field has no rule with a source model, the global rule "
             "is used."
    )

    _sql_constraints = [
        ('model_field_uniq',
         'unique (source_model_id, field_id)',
         'A rule already exists for this field.'),
    ]

    @api.model
    def _domain_source_models(self):
        """ Returns the models for which we can define rules.

        Example for submodules (replace by the xmlid of the model):

        ::
            models = super(ChangesetFieldRule, self)._domain_source_models()
            return models | self.env.ref('base.model_res_users')

        Rules without model are global and apply for all models.

        """
        return self.env.ref('base.model_res_users')

    @api.model
    def _selection_action(self):
        return [('auto', 'Auto'),
                ('validate', 'Validate'),
                ('never', 'Never'),
                ]

    @ormcache(skiparg=1)
    @api.model
    def _get_rules(self, source_model_name):
        """ Cache rules

        Keep only the id of the rules, because if we keep the recordsets
        in the ormcache, we won't be able to browse them once their
        cursor is closed.

        The public method ``get_rules`` return the rules with the recordsets
        when called.

        """
        model_rules = self.search(
            ['|', ('source_model_id.model', '=', source_model_name),
                  ('source_model_id', '=', False)],
            # using 'ASC' means that 'NULLS LAST' is the default
            order='source_model_id ASC',
        )
        # model's rules have precedence over global ones so we iterate
        # over rules which have a source model first, then we complete
        # them with the global rules
        result = {}
        for rule in model_rules:
            # we already have a model's rule
            if result.get(rule.field_id.name):
                continue
            result[rule.field_id.name] = rule.id
        return result

    @api.model
    def get_rules(self, source_model_name):
        """ Return the rules for a model

        When a model is specified, it will return the rules for this
        model.  Fields that have no rule for this model will use the
        global rules (those without source).

        The source model is the model which ask for a change, it will be
        for instance ``res.users``, ``lefac.backend`` or
        ``magellan.backend``.

        The second argument (``source_model_name``) is optional but
        cannot be an optional keyword argument otherwise it would not be
        in the key for the cache. The callers have to pass ``None`` if
        they want only global rules.
        """
        rules = {}
        cached_rules = self._get_rules(source_model_name)
        for field, rule_id in cached_rules.iteritems():
            rules[field] = self.browse(rule_id)
        return rules

    @api.model
    def create(self, vals):
        record = super(ChangesetFieldRule, self).create(vals)
        self.clear_caches()
        return record

    @api.multi
    def write(self, vals):
        result = super(ChangesetFieldRule, self).write(vals)
        self.clear_caches()
        return result

    @api.multi
    def unlink(self):
        result = super(ChangesetFieldRule, self).unlink()
        self.clear_caches()
        return result
