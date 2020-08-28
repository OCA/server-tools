# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class AbstractConditionalImage(models.AbstractModel):
    _name = 'abstract.conditional.image'
    _description = 'Abstract image'

    image = fields.Binary(
        compute='_compute_image', string="Image",
        store=False, readonly=True
    )
    image_medium = fields.Binary(
        compute='_compute_image', string="Medium-sized image",
        store=False, readonly=True
    )
    image_small = fields.Binary(
        compute='_compute_image', string="Small-sized image",
        store=False, readonly=True
    )

    @staticmethod
    def _compute_selector_test_without_company(image_selector, record):
        return bool(
            safe_eval(image_selector.selector or "True", {'object': record})
        )

    @staticmethod
    def _compute_selector_test_with_company(image_selector, record):
        if (image_selector.company_id == record.company_id or
                record.company_id and not image_selector.company_id):
            return AbstractConditionalImage\
                ._compute_selector_test_without_company(
                    image_selector, record
                )
        return False

    def _compute_image(self):
        if 'company_id' in self._fields:
            search_clause = [('model_name', '=', self._name)]
            test_method = self._compute_selector_test_with_company
        else:
            # If inherited object doesn't have a `company_id` field,
            # remove the items with a company defined and the related checks
            search_clause = [('model_name', '=', self._name),
                             ('company_id', '=', False)]
            test_method = self._compute_selector_test_without_company

        image_selectors = self.env['image'].search(
            search_clause, order='company_id, selector'
        )

        for rec in self:
            found = None
            for image_selector in image_selectors:
                if test_method(image_selector, rec):
                    found = image_selector
                    break

            rec.update({
                'image': found and found.image,
                'image_medium': found and found.image_medium,
                'image_small': found and found.image_small,
            })
