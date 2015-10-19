# -*- encoding: utf-8 -*-
# #############################################################################
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2010 - 2014 Savoir-faire Linux
# (<http://www.savoirfairelinux.com>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import StringIO
import base64
import os
import zipfile
from collections import namedtuple

from openerp import fields, models, api


class PrototypeModuleExport(models.TransientModel):
    _name = "module_prototyper.module.export"

    name = fields.Char('File Name', readonly=True)
    api_version = fields.Selection(
        [
            ('8.0', '8.0'),
        ],
        'API version',
        required=True,
        default='8.0'
    )
    data = fields.Binary('File', readonly=True)
    state = fields.Selection(
        [
            ('choose', 'choose'),  # choose version
            ('dep', 'dep'),  # dependencies
            ('get', 'get')  # get module
        ],
        default='choose'
    )

    keep_external_ids = fields.Boolean(
        string="Preserve existing external IDs?",
        help="""Useful, if you are using this module for
        generating module data from different sources.
        Keep for example, when shipping data updates
        with this model. You may well need to still
        manually clean up and mix in the results.""",
        default=False
    )

    fields_selected = fields.Many2many(
        string='Fields Selected',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='ir.model.fields',
        domain=[],
        context={},
        limit=None,
    )

    fields_selected_initial = fields.Many2many(
        string='Fields Selected Difference',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='ir.model.fields',
        domain=[],
        context={},
        limit=None
    )

    fields_not_selected = fields.Many2many(
        string='Fields Not Selected',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='ir.model.fields',
        domain=[],
        context={},
        limit=None,
        compute='_compute_fields_not_selected',
    )

    @api.one
    @api.depends('fields_selected', 'fields_not_selected')
    def _compute_fields_not_selected(self):
        # Diferentes between fields initial and actual
        fields_ini = [field.id for field in self.fields_selected_initial]
        fields_act = [field.id for field in self.fields_selected]
        self.fields_not_selected = list(set(fields_ini) - set(fields_act))

    @api.one
    @api.onchange('fields_not_selected')
    def onchange_fields_not_selected(self):
        # Reformate self.fields_selected (If change fields_not_selected)
        fields_ini = [field.id for field in self.fields_selected_initial]
        fields_diff = [field.id for field in self.fields_not_selected]
        self.fields_selected = list(set(fields_ini) - set(fields_diff))

    @api.model
    def action_export(self, ids):
        """
        Export a zip file containing the module based on the information
        provided in the prototype, using the templates chosen in the wizard.
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        wizard = self.browse(ids)

        active_model = self._context.get('active_model')

        # checking if the wizard was called by a prototype.
        msg = '{} has to be called from a "module_prototyper" , not a "{}"'
        assert active_model == 'module_prototyper', msg.format(
            self, active_model
        )

        # getting the prototype of the wizard
        prototypes = self.env[active_model].browse(
            [self._context.get('active_id')]
        )

        # Validate if are not evaluated the depedencies resolve
        # if the wizard was execute and returned a wizard fields_diff exists
        # if the method dep_resolve not detect ciclyc dependencies
        # (not return a wizard) continue to export files.
        if not wizard.fields_selected and wizard.state != "dep":
            fields_dependencies = self.dep_resolve(wizard, prototypes)

            if fields_dependencies:
                wizard.write(
                    {
                        'fields_selected': [(6, 1, fields_dependencies,)],
                        'fields_selected_initial': [
                            (6, 1, fields_dependencies,)],
                        'state': 'dep',
                    }
                )

                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'module_prototyper.module.export',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': wizard.id,
                    'views': [(False, 'form')],
                    'target': 'new',
                    'context': self._context,
                }

        # Recive of context the fields_not_selected because it's a wizard
        fields_ignore = []
        if 'fields_not_selected' in self._context.keys():
            fields_ignore = self._context['fields_not_selected'][0][2]

        zip_details = self.zip_files(wizard, prototypes, fields_ignore)

        if len(prototypes) == 1:
            zip_name = prototypes[0].name
        else:
            zip_name = "prototyper_export"

        wizard.write(
            {
                'name': '{}.zip'.format(zip_name),
                'state': 'get',
                'data': base64.encodestring(zip_details.stringIO.getvalue())
            }
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'module_prototyper.module.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wizard.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @staticmethod
    def zip_files(wizard, prototypes, fields_ignore=None):
        """Takes a set of file and zips them.
        :param file_details: tuple (filename, file_content)
        :return: tuple (zip_file, stringIO)
        """
        zip_details = namedtuple('Zip_details', ['zip_file', 'stringIO'])
        out = StringIO.StringIO()

        with zipfile.ZipFile(out, 'w') as target:
            for prototype in prototypes:
                # setting the jinja environment.
                # They will help the program to find the template to render the
                # files with.
                prototype.set_jinja_env(wizard.api_version)

                # will let the user decide on the wizard wether he wants
                # to kkep external ids of the modules data or set fresh ones
                prototype.set_keep_external_ids(wizard.keep_external_ids)

                # generate_files ask the prototype to investigate the input and
                # to generate the file templates according to it.  zip_files,
                # in another hand, put all the template files into a package
                # ready to be saved by the user.
                file_details = prototype.generate_files(fields_ignore)
                for filename, file_content in file_details:
                    if isinstance(file_content, unicode):
                        file_content = file_content.encode('utf-8')
                    # Prefix all names with module technical name
                    filename = os.path.join(prototype.name, filename)
                    info = zipfile.ZipInfo(filename)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 2175008768  # specifies mode 0644
                    target.writestr(info, file_content)

            return zip_details(zip_file=target, stringIO=out)

    @api.model
    def dep_resolve(self, wizard, prototypes):
        # This method return a wizard if are ciclyc dependencies,
        # else return void

        fields = []

        # Create a list with field that possible have ciclyc dependencies
        for prototype in prototypes:
            prototype.set_jinja_env(wizard.api_version)
            prototype.set_keep_external_ids(wizard.keep_external_ids)
            fields.extend(prototype.deps_detect())

        return fields
