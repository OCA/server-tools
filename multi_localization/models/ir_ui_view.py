# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia - Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#


from odoo import api, fields, models


class View(models.Model):
    _name = 'ir.ui.view'
    _inherit = 'ir.ui.view'

    localization_ids = fields.Many2many('ir.localization', 'ir_ui_view_localization', 'view_id', 'localization_id',
                                        'Localizations')

    #------------------------------------------------------
    # Inheritance mecanism
    #------------------------------------------------------
    @api.model
    def get_inheriting_views_arch(self, view_id, model):
        res = super(View, self).get_inheriting_views_arch(view_id, model)

        if len(res) == 0:
            #
            # There is no inherited views
            #
            return res

        localization_id = None
        if self.env.user.localization_id:
            localization_id = self.env.user.localization_id.id
        elif self.env.user.company_id and self.env.user.company_id.localization_id:
            localization_id = self.env.user.company_id.localization_id.id

        inherited_view_ids = [inherited_view_id for view_arch, inherited_view_id in res]

        if localization_id is None:
            condition = [
                ['id', 'in', inherited_view_ids],
                ['localization_ids', '=', False],
            ]
        else:
            condition = [
                ['id', 'in', inherited_view_ids],
                '|',
                ['localization_ids', '=', False],
                ['localization_ids', 'in', localization_id],
            ]

        if self.model == 'sped.participante':
            import ipdb; ipdb.set_trace();

        views = self.search(condition)

        if len(views) == len(inherited_view_ids):
            #
            # None of the selected inherited views have any localization limitation
            #
            return res

        if not views:
            return []

        #
        # Some inherited views are limited by localization constraints
        #
        localized_view_ids = [view.id for view in views]
        new_res = []

        for view_arch, inherited_view_id in res:
            if inherited_view_id not in localized_view_ids:
                new_res.append((view_arch, inherited_view_id))

        return new_res

