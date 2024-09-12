# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval


class TierValidation(models.AbstractModel):
    _name = "tier.validation"

    _state_field = 'state'
    _state_from = ['draft']
    _state_to = ['confirmed']
    _cancel_state = 'cancel'

    # TODO: step by step validation?

    review_ids = fields.One2many(
        comodel_name='tier.review', inverse_name='res_id',
        string='Validations',
        domain=lambda self: [('model', '=', self._name)],
        auto_join=True,
    )
    validated = fields.Boolean(
        compute="_compute_validated_rejected",
        search="_search_validated",
    )
    need_validation = fields.Boolean(compute="_compute_need_validation")
    rejected = fields.Boolean(compute="_compute_validated_rejected")
    reviewer_ids = fields.Many2many(
        string="Reviewers", comodel_name="res.users",
        compute="_compute_reviewer_ids",
        search="_search_reviewer_ids",
    )

    can_review = fields.Boolean(compute="_compute_can_review")

    @api.multi
    def _compute_can_review(self):
        for rec in self:
            rec.can_review = self.env.user in rec.reviewer_ids

    @api.multi
    @api.depends('review_ids')
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec.review_ids.filtered(
                lambda r: r.status == 'pending').mapped('reviewer_ids')

    @api.model
    def _search_validated(self, operator, value):
        assert operator in ('=', '!='), 'Invalid domain operator'
        assert value in (True, False), 'Invalid domain value'
        pos = self.search([
            (self._state_field, 'in', self._state_from)]).filtered(
            lambda r: r.review_ids and r.validated == value)
        return [('id', 'in', pos.ids)]

    @api.model
    def _search_reviewer_ids(self, operator, value):
        reviews = self.env['tier.review'].search([
            ('model', '=', self._name),
            ('reviewer_ids', operator, value),
            ('status', '=', 'pending')])
        return [('id', 'in', list(set(reviews.mapped('res_id'))))]

    @api.multi
    def _compute_validated_rejected(self):
        for rec in self:
            rec.validated = self._calc_reviews_validated(rec.review_ids)
            rec.rejected = self._calc_reviews_rejected(rec.review_ids)

    @api.model
    def _calc_reviews_validated(self, reviews):
        """Override for different validation policy."""
        if not reviews:
            return False
        return not any([s != 'approved' for s in reviews.mapped('status')])

    @api.model
    def _calc_reviews_rejected(self, reviews):
        """Override for different rejection policy."""
        return any([s == 'rejected' for s in reviews.mapped('status')])

    @api.multi
    def _compute_need_validation(self):
        for rec in self:
            tiers = self.env[
                'tier.definition'].search([('model', '=', self._name)])
            valid_tiers = any([rec.evaluate_tier(tier) for tier in tiers])
            rec.need_validation = not rec.review_ids and valid_tiers and \
                getattr(rec, self._state_field) in self._state_from

    @api.multi
    def evaluate_tier(self, tier):
        try:
            res = safe_eval(tier.python_code, globals_dict={'rec': self})
        except Exception, error:
            raise UserError(_(
                "Error evaluating tier validation conditions.\n %s") % error)
        return res

    @api.model
    def _get_under_validation_exceptions(self):
        """Extend for more field exceptions."""
        return ['message_follower_ids']

    @api.multi
    def _check_allow_write_under_validation(self, vals):
        """Allow to add exceptions for fields that are allowed to be written
        even when the record is under validation."""
        exceptions = self._get_under_validation_exceptions()
        for val in vals:
            if val not in exceptions:
                return False
        return True

    @api.multi
    def write(self, vals):
        for rec in self:
            if (getattr(rec, self._state_field) in self._state_from and
                    vals.get(self._state_field) in self._state_to):
                if rec.need_validation:
                    # try to validate operation
                    reviews = rec.request_validation()
                    rec._validate_tier(reviews)
                    if not self._calc_reviews_validated(reviews):
                        raise ValidationError(_(
                            "This action needs to be validated for at least "
                            "one record. \nPlease request a validation."))
                if rec.review_ids and not rec.validated:
                    raise ValidationError(_(
                        "A validation process is still open for at least "
                        "one record."))
            if (rec.review_ids and getattr(rec, self._state_field) in
                    self._state_from and not vals.get(self._state_field) in
                    (self._state_to + [self._cancel_state]) and not
                    self._check_allow_write_under_validation(vals)):
                raise ValidationError(_("The operation is under validation."))
        if vals.get(self._state_field) in self._state_from:
            self.mapped('review_ids').unlink()
        return super(TierValidation, self).write(vals)

    def _validate_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status in ('pending', 'rejected') and
            (r.reviewer_id == self.env.user or
             r.reviewer_group_id in self.env.user.groups_id))
        user_reviews.write({'status': 'approved'})

    @api.multi
    def validate_tier(self):
        for rec in self:
            rec._validate_tier()

    @api.multi
    def reject_tier(self):
        for rec in self:
            user_reviews = rec.review_ids.filtered(
                lambda r: r.status in ('pending', 'approved') and
                (r.reviewer_id == self.env.user or
                 r.reviewer_group_id in self.env.user.groups_id))
            user_reviews.write({'status': 'rejected'})

    @api.multi
    def request_validation(self):
        td_obj = self.env['tier.definition']
        tr_obj = created_trs = self.env['tier.review']
        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                if rec.need_validation:
                    tier_definitions = td_obj.search([
                        ('model', '=', self._name)], order="sequence desc")
                    sequence = 0
                    for td in tier_definitions:
                        if self.evaluate_tier(td):
                            sequence += 1
                            created_trs += tr_obj.create({
                                'model': self._name,
                                'res_id': rec.id,
                                'definition_id': td.id,
                                'sequence': sequence,
                            })
                    # TODO: notify? post some msg in chatter?
        return created_trs

    @api.multi
    def restart_validation(self):
        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                rec.mapped('review_ids').unlink()
