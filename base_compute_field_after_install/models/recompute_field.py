# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

DIFFER_COMPUTE_SIZE = 1000


class RecomputeField(models.Model):
    _name = 'recompute.field'
    _description = 'Recompute Field'

    model = fields.Char(required=True)
    field = fields.Char(required=True)
    last_id = fields.Integer()
    step = fields.Integer(required=True, default=1000)
    state = fields.Selection([
        ('todo', 'Todo'),
        ('done', 'Done'),
    ])

    @api.model
    def _run_all(self):
        return self.search([('state', '=', 'todo')]).run()

    def run(self):
        for task in self:
            cursor = self.env.cr
            offset = 0
            model = self.env[task.model]
            if task.last_id:
                domain = [('id', '>', task.last_id)]
            else:
                domain = []
            if task.step <= 0:
                raise UserError(_('Step must by superior to 0'))
            else:
                limit = task.step
            while True:
                _logger.info(
                    'Recompute field %s for model %s in background. Offset %s',
                    task.field, task.model, offset)
                records = model.search(
                    domain, limit=limit, offset=offset, order='id')
                if not records:
                    break
                offset += limit
                field = records._fields[task.field]
                records._recompute_todo(field)
                records.recompute()
                task.last_id = records[-1].id
                cursor.commit()
            task.state = 'done'
            cursor.commit()
        return True


ori_recompute = models.Model.recompute


@api.model
def recompute(self):
    if self.env.context == {'active_test': False}\
            and 'base_compute_field_after_install'\
            in self.env.registry._init_modules:
        for field, recs in self.env.all.todo.items():
            if len(recs[0]) > DIFFER_COMPUTE_SIZE:
                _logger.info(
                    'Differs recomputation of field %s for model %s',
                    field.name, recs[0]._name)
                with self.env.norecompute():
                    self.env['recompute.field'].create({
                        'field': field.name,
                        'model': recs[0]._name,
                        'state': 'todo',
                        })
                map(recs[0]._recompute_done, field.computed_fields)
    return ori_recompute(self)


models.Model.recompute = recompute
