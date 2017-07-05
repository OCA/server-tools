# -*- coding: utf-8 -*-
# Copyright © 2014-2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from openerp import SUPERUSER_ID, models, fields, api, _
from openerp.exceptions import Warning


class IrModel(models.Model):

    _inherit = 'ir.model'
    validator_line_ids = fields.One2many(
        'ir.model.validator.line', 'model_id', 'Validators')

    @api.model
    def check_vals(self, vals, model_name):
        validator_lines = self.env['ir.model.validator.line'].search([
            ('model_id.model', '=', model_name),
            ('field_id.name', 'in', vals.keys())])
        for validator_line in validator_lines:
            pattern = re.compile(validator_line.regex_id.regex)
            if vals[validator_line.field_id.name]:
                if not pattern.match(vals[validator_line.field_id.name]):
                    raise Warning(
                        _('Expression %s not valid for %s') % (
                            validator_line.regex_id.regex,
                            vals[validator_line.field_id.name]))
        return True

    def _field_validator_hook(self, cr, ids):

        def _wrap_create():
            def create(self, cr, uid, vals, context=None, **kwargs):
                model_pool = self.pool['ir.model']
                model_pool.check_vals(
                    cr, uid, vals, self._name, context=context)
                new_id = create.origin(
                    self, cr, uid, vals, context=context, **kwargs)
                return new_id
            return create

        def _wrap_write():
            def write(self, cr, uid, ids, vals, context=None, **kwargs):
                model_pool = self.pool['ir.model']
                model_pool.check_vals(
                    cr, uid, vals, self._name, context=context)
                res = write.origin(
                    self, cr, uid, ids, vals, context=context, **kwargs)
                return res
            return write

        for model in self.browse(cr, SUPERUSER_ID, ids):
            if model.validator_line_ids:
                model_name = model.model
                model_obj = self.pool.get(model_name)
                if model_obj and not hasattr(
                    model_obj, 'field_validator_checked'
                ):
                    model_obj._patch_method('create', _wrap_create())
                    model_obj._patch_method('write', _wrap_write())
                    model_obj.field_validator_checked = True
        return True

    def _register_hook(self, cr):
        self._field_validator_hook(cr, self.search(cr, SUPERUSER_ID, []))
        return super(IrModel, self)._register_hook(cr)

    def create(self, cr, uid, vals, context=None):
        res_id = super(IrModel, self).create(
            cr, uid, vals, context=context)
        self._field_validator_hook(cr, [res_id])
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(IrModel, self).write(cr, uid, ids, vals, context=context)
        self._field_validator_hook(cr, ids)
        return res


class IrModelValidatorLine(models.Model):
    _name = "ir.model.validator.line"
    _rec_name = 'model_id'
    model_id = fields.Many2one('ir.model', string="Model", required=True)
    field_id = fields.Many2one('ir.model.fields', 'Field', required=True)
    regex_id = fields.Many2one(
        'ir.model.fields.regex', string="Validator", required=True)
