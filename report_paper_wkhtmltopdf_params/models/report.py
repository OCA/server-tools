# -*- coding: utf-8 -*-
# Copyright 2017 Avoin.Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class Report(models.Model):
    _inherit = 'report'

    def _build_wkhtmltopdf_args(self, paperformat,
                                specific_paperformat_args=None):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        command_args = super(Report, self)._build_wkhtmltopdf_args(
            paperformat,
            specific_paperformat_args
        )

        for param in paperformat.custom_params:
            command_args.extend([param.name])
            if param.value:
                command_args.extend([param.value])

        return command_args
