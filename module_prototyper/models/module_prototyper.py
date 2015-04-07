# -*- encoding: utf-8 -*-
# #############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
import os
import re
import base64
from datetime import date

from collections import namedtuple
from jinja2 import Environment, FileSystemLoader
from openerp import models, api, fields
from .default_description import get_default_description
YEAR = date.today().year


class ModulePrototyper(models.Model):
    """Module Prototyper gathers different information from all over the
    database to build a prototype of module.
    We are calling it a prototype as it will most likely need to be reviewed
    by a developer to fix glitch that would sneak it during the generation of
    files but also to add not supported features.
    """
    _name = "module_prototyper"
    _description = "Module Prototyper"

    license = fields.Selection(
        [('GPL-2', 'GPL Version 2'),
         ('GPL-2 or any later version', 'GPL-2 or later version'),
         ('GPL-3', 'GPL Version 3'),
         ('GPL-3 or any later version', 'GPL-3 or later version'),
         ('AGPL-3', 'Affero GPL-3'),
         ('Other OSI approved licence', 'Other OSI Approved Licence'),
         ('Other proprietary', 'Other Proprietary')],
        string='License',
        default='AGPL-3',
    )
    name = fields.Char(
        'Technical Name', required=True,
        help=('The technical name will be used to define the name of '
              'the exported module, the name of the model.')
    )
    category_id = fields.Many2one('ir.module.category', 'Category')
    human_name = fields.Char(
        'Module Name', required=True,
        help=('The Module Name will be used as the displayed name of the '
              'exported module.')
    )
    summary = fields.Char('Summary', required=True,
                          help=('Enter a summary of your module'))
    description = fields.Text(
        'Description',
        required=True,
        help=('Enter the description of your module, what it does, how to'
              'install, configure and use it, the roadmap or known issues.'
              'The description will be exported in README.rst'),
        default=get_default_description
    )
    author = fields.Char('Author', required=True, help=('Enter your name'))
    maintainer = fields.Char(
        'Maintainer',
        help=('Enter the name of the person or organization who will'
              'maintain this module')
    )
    website = fields.Char('Website', help=('Enter the URL of your website'))
    icon_image = fields.Binary(
        'Icon',
        help=('The icon set up here will be used as the icon '
              'for the exported module also')
    )
    version = fields.Char(
        'Version',
        size=3,
        default='0.1',
        help=('Enter the version of your module with 2 digits')
    )
    auto_install = fields.Boolean(
        'Auto Install',
        default=False,
        help='Check if the module should be install by default.'
    )
    application = fields.Boolean(
        'Application',
        default=False,
        help='Check if the module is an Odoo application.'
    )
    # Relations
    dependency_ids = fields.Many2many(
        'ir.module.module', 'module_prototyper_module_rel',
        'module_prototyper_id', 'module_id',
        'Dependencies',
        help=('Enter the list of required modules that need to be installed'
              'for your module to work properly')
    )
    data_ids = fields.Many2many(
        'ir.filters',
        'prototype_data_rel',
        'module_prototyper_id', 'filter_id',
        'Data filters',
        help="The records matching the filters will be added as data."
    )
    demo_ids = fields.Many2many(
        'ir.filters',
        'prototype_demo_rel',
        'module_prototyper_id', 'filter_id',
        'Demo filters',
        help="The records matching the filters will be added as demo data."
    )
    field_ids = fields.Many2many(
        'ir.model.fields', 'prototype_fields_rel',
        'module_prototyper_id', 'field_id', 'Fields',
        help=('Enter the list of fields that you have created or modified'
              'and want to export in this module. New models will be'
              'exported as long as you choose one of his fields.')
    )
    menu_ids = fields.Many2many(
        'ir.ui.menu', 'prototype_menu_rel',
        'module_prototyper_id', 'menu_id', 'Menu Items',
        help=('Enter the list of menu items that you have created and want'
              'to export in this module. Related windows actions will be'
              'exported as well.')
    )
    view_ids = fields.Many2many(
        'ir.ui.view', 'prototype_view_rel',
        'module_prototyper_id', 'view_id', 'Views',
        help=('Enter the list of views that you have created and want to'
              'export in this module.')
    )
    group_ids = fields.Many2many(
        'res.groups', 'prototype_groups_rel',
        'module_prototyper_id', 'group_id', 'Groups',
        help=('Enter the list of groups that you have created and want to'
              'export in this module.')
    )
    right_ids = fields.Many2many(
        'ir.model.access', 'prototype_rights_rel',
        'module_prototyper_id', 'right_id',
        'Access Rights',
        help=('Enter the list of access rights that you have created and'
              'want to export in this module.')
    )
    rule_ids = fields.Many2many(
        'ir.rule', 'prototype_rule_rel',
        'module_prototyper_id', 'rule_id', 'Record Rules',
        help=('Enter the list of record rules that you have created and'
              'want to export in this module.')
    )

    __data_files = []
    __field_descriptions = {}
    _env = None
    File_details = namedtuple('file_details', ['filename', 'filecontent'])
    template_path = '{}/../templates/'.format(os.path.dirname(__file__))

    @api.model
    def set_jinja_env(self, api_version):
        """Set the Jinja2 environment.
        The environment will helps the system to find the templates to render.
        :param api_version: string, odoo api
        :return: jinja2.Environment instance.
        """
        if self._env is None:
            self._env = Environment(
                loader=FileSystemLoader(
                    os.path.join(self.template_path, api_version)
                )
            )
        return self._env

    def set_field_descriptions(self):
        """Mock the list of fields into dictionary.
        It allows us to add or change attributes of the fields.

        :return: None
        """
        for field in self.field_ids:
            field_description = {}
            # This will mock a field record.
            # the mock will allow us to add data or modify the data
            # of the field (like for the name) with keeping all the
            # attributes of the record.
            field_description.update({
                attr_name: getattr(field, attr_name)
                for attr_name in dir(field)
                if not attr_name[0] == '_'
            })
            # custom fields start with the prefix x_.
            # it has to be removed.
            field_description['name'] = re.sub(r'^x_', '', field.name)
            self.__field_descriptions[field] = field_description

    @api.model
    def generate_files(self):
        """ Generates the files from the details of the prototype.
        :return: tuple
        """
        assert self._env is not None, \
            'Run set_env(api_version) before to generate files.'

        self.set_field_descriptions()
        file_details = []
        file_details.extend(self.generate_models_details())
        file_details.extend(self.generate_views_details())
        file_details.extend(self.generate_menus_details())
        file_details.append(self.generate_module_init_file_details())
        # must be the last as the other generations might add information
        # to put in the __openerp__: additional dependencies, views files, etc.
        file_details.append(self.generate_module_openerp_file_details())
        if self.icon_image:
            file_details.append(self.save_icon())

        return file_details

    @api.model
    def save_icon(self):
        """Save the icon of the prototype as a image.
        The image is used afterwards as the icon of the exported module.

        :return: FileDetails instance
        """
        # TODO: The image is not always a jpg.
        # 2 ways to do it:
        #   * find a way to detect image type from the data
        #   * add document as a dependency.
        # The second options seems to be better, as Document is a base module.
        return self.File_details(
            os.path.join('static', 'description', 'icon.jpg'),
            base64.b64decode(self.icon_image)
        )

    @api.model
    def generate_module_openerp_file_details(self):
        """Wrapper to generate the __openerp__.py file of the module."""
        return self.generate_file_details(
            '__openerp__.py',
            '__openerp__.py.template',
            prototype=self,
            data_files=self.__data_files,
        )

    @api.model
    def generate_module_init_file_details(self):
        """Wrapper to generate the __init__.py file of the module."""
        return self.generate_file_details(
            '__init__.py',
            '__init__.py.template',
            # no import models if no work of fields in
            # the prototype
            models=bool(self.field_ids)
        )

    @api.model
    def generate_models_details(self):
        """Finds the models from the list of fields and generates
        the __init__ file and each models files (one by class).
        """
        files = []
        # TODO: doesn't work as need to find the module to import
        # and it is not necessary the name of the model the fields
        # belongs to.
        # ie. field.cell_phone is defined in a model inheriting from
        # res.partner.
        # How do we find the module the field was defined in?
        # dependencies = set([dep.id for dep in self.dependencies])

        relations = {}
        for field in self.__field_descriptions.itervalues():
            model = field.get('model_id')
            relations.setdefault(model, []).append(field)
            # dependencies.add(model.id)

        # blind update of dependencies.
        # self.write({
        #     'dependencies': [(6, 0, [id_ for id_ in dependencies])]
        # })

        files.append(self.generate_models_init_details(relations.keys()))
        for model, custom_fields in relations.iteritems():
            files.append(self.generate_model_details(model, custom_fields))

        return files

    @api.model
    def generate_models_init_details(self, ir_models):
        """Wrapper to generate the __init__.py file in models folder."""
        return self.generate_file_details(
            'models/__init__.py',
            'models/__init__.py.template',
            models=[
                self.friendly_name(ir_model.model)
                for ir_model in ir_models
            ]
        )

    @api.model
    def generate_views_details(self):
        """Wrapper to generate the views files."""
        relations = {}
        for view in self.view_ids:
            relations.setdefault(view.model, []).append(view)

        views_details = []
        for model, views in relations.iteritems():
            filepath = 'views/{}_view.xml'.format(
                self.friendly_name(model)
            )
            views_details.append(
                self.generate_file_details(
                    filepath,
                    'views/model_views.xml.template',
                    views=views
                )
            )
            self.__data_files.append(filepath)

        return views_details

    @api.model
    def generate_menus_details(self):
        """Wrapper to generate the menus files."""
        relations = {}
        for menu in self.menu_ids:
            relations.setdefault(menu.action.res_model, []).append(menu)

        menus_details = []
        for model_name, menus in relations.iteritems():
            filepath = 'views/{}_menus.xml'.format(
                self.friendly_name(model_name)
            )
            menus_details.append(
                self.generate_file_details(
                    filepath,
                    'views/model_menus.xml.template',
                    menus=menus,
                )
            )
            self.__data_files.append(filepath)

        return menus_details

    @api.model
    def generate_model_details(self, model, field_descriptions):
        """Wrapper to generate the python file for the model.

        :param model: ir.model record.
        :param field_descriptions: list of ir.model.fields records.
        :return: FileDetails instance.
        """
        python_friendly_name = self.friendly_name(model.model)
        return self.generate_file_details(
            'models/{}.py'.format(python_friendly_name),
            'models/model_name.py.template',
            name=python_friendly_name,
            inherit=model.model,
            fields=field_descriptions,
        )

    @staticmethod
    def friendly_name(name):
        return name.replace('.', '_')

    @api.model
    def generate_file_details(self, filename, template, **kwargs):
        """ generate file details from jinja2 template.
        :param filename: name of the file the content is related to
        :param template: path to the file to render the content
        :param kwargs: arguments of the template
        :return: File_details instance
        """
        template = self._env.get_template(template)
        # keywords used in several templates.
        kwargs.update(
            {
                'export_year': YEAR,
                'author': self.author,
                'website': self.website,
                'cr': self._cr,
            }
        )
        return self.File_details(filename, template.render(kwargs))
