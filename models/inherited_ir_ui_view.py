# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_resource_from_path
from odoo.tools.parse_version import parse_version
from odoo.tools.view_validation import valid_view
from odoo.tools.translate import encode


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    copy_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string=u'Copied View',
        ondelete='restrict',
        index=True,
    )

    @api.model
    def create(self, values):
        #
        # Ensures that the arch of the copied view is realy copied from the
        # original view
        #
        if values.get('copy_id'):
            values['arch'] = self.browse(values['copy_id']).arch

        return super(IrUiView, self).create(values)

    @api.model
    def write(self, values):
        copied_views = []

        for view in self:
            #
            # Saves copied views for latter proccess
            #
            cv = self.search([('copy_id', '=', view.id)])
            if cv:
                copied_views += [[view.id, cv]]

            #
            # Ensures that the arch of the copied view remains copied from the
            # original view
            #
            if values.get('copy_id'):
                values['arch'] = self.browse(values['copy_id']).arch

        res = super(IrUiView, self).write(values)

        if copied_views:
            for view_id, cv in copied_views:
                view = self.browse(view_id)
                cv.write({'arch': view.arch})

        return res

    @api.constrains('arch_db')
    def _check_xml(self):
        for view in self:
            #
            # When the view is being copied, there's no need to validate it's
            # arch, because the original view has already been validated
            #
            if view.copy_id:
                continue

            super(IrUiView, view)._check_xml()

        return True
