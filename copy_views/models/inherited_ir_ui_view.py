# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#


from odoo import api, fields, models


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    copy_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string='Copied View',
        ondelete='restrict',
        index=True,
    )
    copy_children_ids = fields.One2many(
        comodel_name='ir.ui.view',
        inverse_name='copy_id',
        string='Views which copy from this one',
    )

    @api.model
    def create(self, values):
        #
        # Ensures that the arch of the copied view is really copied from the
        # original view
        #
        if values.get('copy_id'):
            copied_view = self.browse(values['copy_id'])
            values['arch'] = copied_view.read_combined(['arch'])['arch']

        res = super(IrUiView, self).create(values)

        #
        # Ensures inheritance gets replicated to copied views
        #
        if values.get('inherit_id'):
            cv = self.search([('copy_id', '=', res.inherit_id.id)])
            arch = res.read_combined(['arch'])['arch']
            for view in cv:
                view.write({'arch': arch})

        return res

    @api.multi
    def write(self, values):
        copied_views = []

        for view in self:
            #
            # Saves copied views for later process
            #
            cv = self.search([('copy_id', '=', view.id)])
            if cv:
                copied_views += [[view.id, cv]]

            #
            # Saves copied views for later process
            #
            if values.get('inherit_id'):
                cv = self.search([('copy_id', '=', values['inherit_id'])])
                if cv:
                    copied_views += [[view.id, cv]]

            #
            # Ensures that the arch of the copied view remains copied from the
            # original view
            #
            if values.get('copy_id'):
                copied_view = self.browse(values['copy_id'])
                values['arch'] = copied_view.read_combined(['arch'])['arch']

        res = super(IrUiView, self).write(values)

        if copied_views:
            for view_id, cv in copied_views:
                view = self.browse(view_id)
                arch = view.read_combined(['arch'])['arch']
                for view in cv:
                    view.write({'arch': arch})

        return res

    @api.multi
    def unlink(self):
        copied_views = []

        for view in self:
            if not view.inherit_id:
                continue

            #
            # Saves copied views for later process
            #
            cv = self.search([('copy_id', '=', view.inherit_id.id)])
            if cv:
                copied_views += [[view.inherit_id.id, cv]]

        res = super(IrUiView, self).unlink()

        #
        # Adjusts now the copies of the inherited views
        #
        if copied_views:
            for view_id, cv in copied_views:
                inherited_view_ids = \
                    self.search([('inherit_id', '=', view_id)])

                if len(inherited_view_ids) > 0:
                    view = self.browse(inherited_view_ids[0])
                else:
                    view = self.browse(view_id)

                arch = view.read_combined(['arch'])['arch']
                for view in cv:
                    view.write({'arch': arch})

        return res

    @api.constrains('arch_db')
    def _check_xml(self):
        for view in self:
            #
            # When the view is being copied, there's no need to validate its
            # arch, because the original view has already been validated
            #
            if view.copy_id:
                continue

            super(IrUiView, view)._check_xml()

        return True
