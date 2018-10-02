# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import fields, models
from openerp.tools.safe_eval import safe_eval


class AbstractImageStorage(models.AbstractModel):
    _name = 'abstract.conditional.image'

    image = fields.Binary(
        compute='_compute_image', string="Image",
        store=False, readonly=True
    )
    image_medium = fields.Binary(
        compute='_compute_image', string="Image",
        store=False, readonly=True
    )
    image_small = fields.Binary(
        compute='_compute_image', string="Image",
        store=False, readonly=True
    )

    def _compute_image(self):
        if 'company_id' in self._fields:
            images = self.env['image'].search(
                [('model_name', '=', self._name)],
                order='company_id, selector'
            )
            def test_method(image, rec):
                return ((image.company_id == rec.company_id or
                         rec.company_id and not image.company_id) and
                        safe_eval(image.selector or "True", {'object': rec}))
        else:
            # If inherited object doesn't have a `company_id` field,
            # remove the items with a company defined and the related checks
            images = self.env['image'].search(
                [('model_name', '=', self._name),
                 ('company_id', '=', False)],
                order='company_id, selector'
            )
            def test_method(image, rec):
                return safe_eval(image.selector or "True", {'object': rec})

        for rec in self:
            found = None
            for image in images:
                if test_method(image, rec):
                    found = image
                    break

            rec.update({
                'image': found and found.image,
                'image_medium': found and found.image_medium,
                'image_small': found and found.image_small,
            })
