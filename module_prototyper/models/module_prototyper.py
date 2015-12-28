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
import base64
import logging
import lxml.etree
import os
import re
import textwrap

from collections import namedtuple
from datetime import date

from jinja2 import Environment, FileSystemLoader

from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval
from openerp.exceptions import ValidationError

from . import licenses

_logger = logging.getLogger(__name__)

YEAR = date.today().year


class IrFilter(models.Model):
    _inherit = 'ir.filters'

    sequence = fields.Integer()


class ModulePrototyper(models.Model):

    """Module Prototyper gathers different information from all over the
    database to build a prototype of module.
    We are calling it a prototype as it will most likely need to be reviewed
    by a developer to fix glitch that would sneak it during the generation of
    files but also to add not supported features.
    """
    _name = "module_prototyper"
    _description = "Module Prototyper"

    def get_default_description(self):
        """
        Extract the content of default description
        """
        filepath = '{}/../data/README.rst'.format(os.path.dirname(__file__))
        with open(filepath, 'r') as content_file:
            content = content_file.read()
        return content

    license = fields.Selection(
        [
            (licenses.GPL3, 'GPL Version 3'),
            (licenses.GPL3_L, 'GPL-3 or later version'),
            (licenses.LGPL3, 'LGPL-3'),
            (licenses.LGPL3_L, 'LGPL-3 or later version'),
            (licenses.AGPL3, 'Affero GPL-3'),
            (licenses.OSI, 'Other OSI Approved Licence'),
            ('Other proprietary', 'Other Proprietary')
        ],
        string='License',
        default=licenses.AGPL3,
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
        help=('Enter the description of your module, what it does, how to '
              'install, configure and use it, the roadmap or known issues. '
              'The description will be exported in README.rst'),
        default=get_default_description
    )
    author = fields.Char('Author', required=True, help=('Enter your name'))
    maintainer = fields.Char(
        'Maintainer',
        help=('Enter the name of the person or organization who will '
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
        size=9,
        default='8.0.1.0.0',
        help=('Enter the version of your module with 5 digits')
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
        help=('Enter the list of required modules that need to be installed '
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
        help=('Enter the list of fields that you have created or modified '
              'and want to export in this module. New models will be '
              'exported as long as you choose one of his fields.')
    )
    menu_ids = fields.Many2many(
        'ir.ui.menu', 'prototype_menu_rel',
        'module_prototyper_id', 'menu_id', 'Menu Items',
        help=('Enter the list of menu items that you have created and want '
              'to export in this module. Related windows actions will be '
              'exported as well.')
    )
    view_ids = fields.Many2many(
        'ir.ui.view', 'prototype_view_rel',
        'module_prototyper_id', 'view_id', 'Views',
        help=('Enter the list of views that you have created and want to '
              'export in this module.')
    )
    group_ids = fields.Many2many(
        'res.groups', 'prototype_groups_rel',
        'module_prototyper_id', 'group_id', 'Groups',
        help=('Enter the list of groups that you have created and want to '
              'export in this module.')
    )
    right_ids = fields.Many2many(
        'ir.model.access', 'prototype_rights_rel',
        'module_prototyper_id', 'right_id',
        'Access Rights',
        help=('Enter the list of access rights that you have created and '
              'want to export in this module.')
    )
    rule_ids = fields.Many2many(
        'ir.rule', 'prototype_rule_rel',
        'module_prototyper_id', 'rule_id', 'Record Rules',
        help=('Enter the list of record rules that you have created and '
              'want to export in this module.')
    )
    report_ids = fields.Many2many(
        'ir.actions.report.xml', 'prototype_report_rel',
        'module_prototyper_id', 'report_id', 'Reports',
        help=('Enter the list of reports that you have created and '
              'want to export in this module.')
    )
    activity_ids = fields.Many2many(
        'workflow.activity', 'prototype_wf_activity_rel',
        'module_prototyper_id', 'activity_id', 'Activities',
        help=('Enter the list of workflow activities that you have created '
              'and want to export in this module')
    )
    transition_ids = fields.Many2many(
        'workflow.transition', 'prototype_wf_transition_rel',
        'module_prototyper_id', 'transition_id', 'Transitions',
        help=('Enter the list of workflow transitions that you have created '
              'and want to export in this module')
    )
    keep_external_ids = fields.Boolean(default=False)

    _env = None
    _data_files = ()
    _demo_files = ()
    _field_descriptions = None
    File_details = namedtuple('file_details', ['filename', 'filecontent'])
    template_path = '{}/../templates/'.format(os.path.dirname(__file__))
    MAGIC_FIELDS_KEY = ["create_date", "create_uid", "write_uid", "id",
                        "__last_update", "write_date", "display_name", "image"]
    type_fields = ["xml", "html", "file", "char", "base64",
                   "int", "float", "list", "tuple"]

    @api.model
    def set_keep_external_ids(self, bool):
        """Set the the keep_external_ids from the wizard
        keep_external_ids will help to update all external
        ids or keep exsting ones.
        :param bool: bool, wizard's value
        """
        self.keep_external_ids = bool
        pass

    @api.model
    def set_jinja_env(self, api_version):
        """Set the Jinja2 environment.
        The environment will helps the system to find the templates to render.
        :param api_version: string, odoo api
        :return: jinja2.Environment instance.
        """
        if self._env is None:
            self._env = Environment(
                lstrip_blocks=True,
                trim_blocks=True,
                loader=FileSystemLoader(
                    os.path.join(self.template_path, api_version)
                )
            )
            # Instanse methods that will be sent to file
            self._env.globals.update({'len': len})
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
            field_description['name'] = self.unprefix(field.name)
            self._field_descriptions[field] = field_description

    @api.model
    def generate_files(self, fields_ignore=None):
        """ Generates the files from the details of the prototype.
        :return: tuple
        """
        assert self._env is not None, \
            'Run set_env(api_version) before to generate files.'

        # Avoid sharing these across instances
        self._data_files = []
        self._demo_files = []
        self._field_descriptions = {}
        self.set_field_descriptions()
        file_details = []
        file_details.extend(self.generate_models_details())
        file_details.extend(self.generate_views_details())
        file_details.extend(self.generate_menus_details())
        file_details.append(self.generate_module_init_file_details())
        file_details.extend(self.generate_data_files(fields_ignore))
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
            data_files=self._data_files,
            demo_fiels=self._demo_files,
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
        """
        Finds the models from the list of fields and generates
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
        field_descriptions = self._field_descriptions or {}
        for field in field_descriptions.itervalues():
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
                self.friendly_name(self.unprefix(model))
            )
            views_details.append(
                self.generate_file_details(
                    filepath,
                    'views/model_views.xml.template',
                    views=views
                )
            )
            self._data_files.append(filepath)

        return views_details

    @api.model
    def generate_menus_details(self):
        """Wrapper to generate the menus files."""
        relations = {}
        for menu in self.menu_ids:
            if menu.action and menu.action.res_model:
                model = self.unprefix(menu.action.res_model)
            else:
                model = 'ir_ui'
            relations.setdefault(model, []).append(menu)

        menus_details = []
        for model_name, menus in relations.iteritems():
            model_name = self.unprefix(model_name)
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
            self._data_files.append(filepath)

        return menus_details

    @api.model
    def generate_model_details(self, model, field_descriptions):
        """Wrapper to generate the python file for the model.

        :param model: ir.model record.
        :param field_descriptions: list of ir.model.fields records.
        :return: FileDetails instance.
        """
        python_friendly_name = self.friendly_name(self.unprefix(model.model))
        return self.generate_file_details(
            'models/{}.py'.format(python_friendly_name),
            'models/model_name.py.template',
            name=python_friendly_name,
            model=model,
            fields=field_descriptions,
        )

    def topological_sort(self, items):
        """
        Items must be provided in the form of an iterable,
        where the key has a tuple.
        [
        [item,[dependencies]],
        [,[]],
        [,[]]
        ]
        """
        provided = set()
        while items:
            remaining_items = []
            emitted = False

            for item, dependencies, records in items:
                #
                # Definir el metodo que ignora los fields_diff
                #
                if dependencies.issubset(provided):
                    yield item, records
                    provided.add(item)
                    emitted = True
                else:
                    remaining_items.append((item, dependencies, records))

            if not emitted:
                raise ValidationError('The dependency-aware sorting\
                    (topological sort) of the model names faild.\
                    Probably the algorythm is getting a circular dependency.\
                    Please refer to the source code.')

            items = remaining_items

    @api.model
    def generate_data_files(self, fields_ignore=None):
        """ Generate data and demo files """
        data, demo = {}, {}
        filters = [
            (data, ir_filter)
            for ir_filter in self.data_ids
        ] + [
            (demo, ir_filter)
            for ir_filter in self.demo_ids
        ]

        for target, ir_filter in filters:
            model = ir_filter.model_id
            model_obj = self.env[model]
            target.setdefault(model, model_obj.browse([]))
            target[model] |= model_obj.search(safe_eval(ir_filter.domain))

        res = []

        # Contains name of fields that will ignored
        fields_obj = self.env['ir.model.fields']
        fields_ignore_names = [field.name for field in
                               fields_obj.browse(fields_ignore)]

        for prefix, model_data, file_list in [
                ('data', data, self._data_files),
                ('demo', demo, self._demo_files)]:

            items = []
            models = set(m for m, recs in model_data.iteritems())

            for model_name, records in model_data.iteritems():
                if not records:
                    raise ValidationError('There are no records\
                     on a particular filter. Please check, that you\'re\
                      only accessing filters that show records.')
                dependencies = set()
                for f in records._fields:
                    if f in fields_ignore_names:
                        continue
                    d = records._fields[f].comodel_name
                    if d is not None and d in models and d != model_name:
                        dependencies.add(d)
                # ensure unique values of comodel_types
                items.append([model_name, dependencies, records])

            for model_name, records in self.topological_sort(items):
                fname = self.friendly_name(self.unprefix(model_name))
                filename = '{0}/{1}.xml'.format(prefix, fname)
                self._data_files.append(filename)
                records = self.fixup_data(records)

                res.append(self.generate_file_details(
                    filename,
                    'data/model_name.xml.template',
                    model=model_name,
                    records=records,
                ))

        return res

    @classmethod
    def unprefix(cls, name):
        if not name:
            return name
        return re.sub('^x_', '', name)

    @classmethod
    def is_prefixed(cls, name):
        return bool(re.match('^x_', name))

    @classmethod
    def friendly_name(cls, name):
        return name.replace('.', '_')

    @classmethod
    def fixup_domain(cls, domain):
        """ Fix a domain according to unprefixing of fields """
        res = []
        for elem in domain:
            if len(elem) == 3:
                elem = list(elem)
                elem[0] = cls.unprefix(elem[0])
            res.append(elem)
        return res

    @classmethod
    def fixup_arch(cls, archstr):
        doc = lxml.etree.fromstring(archstr)
        for elem in doc.xpath("//*[@name]"):
            elem.attrib["name"] = cls.unprefix(elem.attrib["name"])

        for elem in doc.xpath("//*[@attrs]"):
            try:
                attrs = safe_eval(elem.attrib["attrs"])
            except Exception:
                _logger.error("Unable to eval attribute: %s, skipping",
                              elem.attrib["attrs"])
                continue

            if isinstance(attrs, dict):
                for key, val in attrs.iteritems():
                    if isinstance(val, (list, tuple)):
                        attrs[key] = cls.fixup_domain(val)
                elem.attrib["attrs"] = repr(attrs)

        for elem in doc.xpath("//field"):
            # Make fields self-closed by removing useless whitespace
            if elem.text and not elem.text.strip():
                elem.text = None

        return lxml.etree.tostring(doc)

    @classmethod
    def order_data(cls, records):

        x = max([r.id for r in records])

        def key(record):
            level = 0

            if hasattr(record, 'parent_id'):
                parent = record.parent_id or False

                while parent:
                    level += 1
                    parent = hasattr(parent, 'parent_id') and parent.parent_id

            return (level * x) + record.id

        return records.sorted(key=key)

    @api.model
    def generate_external_id(self, records):
        ir_model_data = records.sudo().env['ir.model.data']
        i = 0
        x = max([r.id for r in records])
        n = len(str(x))

        if not self.keep_external_ids:
            delete = ir_model_data.search([('model', '=', records._name)])
            delete.unlink()

        for r in records:
            i += 1
            data = ir_model_data.search(
                [('model', '=', r._name), ('res_id', '=', r.id)])

            if data and self.keep_external_ids:
                pass
            elif not self.keep_external_ids:
                name = '%s_%s' % (r._name.split(".").pop(), str(i).zfill(n))
                ir_model_data.create({
                    'model': r._name,
                    'res_id': r.id,
                    'module': self.name,
                    'name': name,
                })

    @api.model
    def fixup_data(cls, records):
        records = cls.order_data(records)
        cls.generate_external_id(records)

        # http://odoo-80.readthedocs.org/en/latest/reference/data.html
        # http://stackoverflow.com/questions/26011102/openerp-odoo-model-relationship-xml-syntax
        # For simplicity, we might be able to work with the eval and the obj,
        # that is available in the context and browse it by the id,
        # that we already have

        recs_lst = []
        for r in records:
            ext_id = r.get_external_id().values()[0]
            fields_lst = []

            for field, val in r.read()[0].iteritems():
                if field in cls.MAGIC_FIELDS_KEY:
                    continue

                ref = False
                field_type = False

                # Only catch external ids, if it is a relational field
                # TODO: Verify, if fields._RelationalMulti (One2many&Many2many)
                # are also represented in an xml with the ref attribute
                # Else there would need to be added an if statement which
                # constructs the eval attribute accordingly.
                if isinstance(r._fields[field], fields._Relational):
                    ref = ",".join(r[field].get_external_id().values())
                    val = False

                # see:https://www.odoo.com/documentation/8.0/reference/data.html
                if r.fields_get()[field]['type'] in cls.type_fields:
                    field_type = r.fields_get()[field]['type']

                # Ref data to list
                # If name of module is in ref it is deleted
                # (Data fields not referring to himself)
                if ref and cls.name in ref:
                    ref = ref.replace(cls.name + ".", "")
                    ref = ref.split(",")
                elif ref:
                    ref = ref.split(",")
                else:
                    ref = []

                fields_lst.append([field, val, ref, field_type])

            # Ordering fields on each record in alfabetical order.
            fields_lst = sorted(fields_lst, key=lambda k: k[0])
            # add external id and fields list to rec_lst
            recs_lst.extend([(ext_id, fields_lst)])

        return sorted(recs_lst, key=lambda k: k[0])

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
                'export_year': date.today().year,
                'author': self.author,
                'website': self.website,
                'license_text': licenses.get_license_text(self.license),
                'cr': self._cr,
                # Utility functions
                'fixup_arch': self.fixup_arch,
                'is_prefixed': self.is_prefixed,
                'unprefix': self.unprefix,
                'wrap': wrap,

            }
        )
        return self.File_details(filename, template.render(kwargs))

    @api.model
    def deps_detect(self):
        """ Detect depedencies of the data fields.
        :return: list
        """

        assert self._env is not None, \
            'Run set_env(api_version) before to generate files.'

        self.generate_models_details()

        data, demo = {}, {}
        filters = [
            (data, ir_filter)
            for ir_filter in self.data_ids
        ] + [
            (demo, ir_filter)
            for ir_filter in self.demo_ids
        ]

        for target, ir_filter in filters:
            model = ir_filter.model_id
            model_obj = self.env[model]
            target.setdefault(model, model_obj.browse([]))
            target[model] |= model_obj.search(safe_eval(ir_filter.domain))

        fields_dep = []
        fields_obj = self.env['ir.model.fields']
        model_obj = self.env['ir.model']

        for prefix, model_data, file_list in [
                ('data', data, self._data_files),
                ('demo', demo, self._demo_files)]:

            models = set(m for m, recs in model_data.iteritems())

            for model_name, records in model_data.iteritems():
                if not records:
                    raise ValidationError('There are no records on a\
                                particular filter. Please check,\
                                that you\'re only accessing filters\
                                that show records.')
                for f in records._fields:
                    dep = records._fields[f].comodel_name
                    if dep is not None and dep in models and dep != model_name:
                        # Save fields that possibly contains circular
                        # dependency
                        model_id = model_obj.search(
                            [['model', '=', model_name]]).id
                        field_id = fields_obj.search(
                            [['name', '=', f],
                             ['model_id', '=', model_id]])
                        fields_dep.append(field_id.id)

        return fields_dep


# Utility functions for rendering templates
def wrap(text, **kwargs):
    """ Wrap some text for inclusion in a template, returning lines

    keyword arguments available, from textwrap.TextWrapper:

        width=70
        initial_indent=''
        subsequent_indent=''
        expand_tabs=True
        replace_whitespace=True
        fix_sentence_endings=False
        break_long_words=True
        drop_whitespace=True
        break_on_hyphens=True
    """
    if not text:
        return []
    wrapper = textwrap.TextWrapper(**kwargs)
    # We join the lines and split them again to offer a stable api for
    # the jinja2 templates, regardless of replace_whitspace=True|False
    text = "\n".join(wrapper.wrap(text))
    return text.splitlines()
