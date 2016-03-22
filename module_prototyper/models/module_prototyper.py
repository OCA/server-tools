# -*- coding: utf-8 -*-
# © 2010 - 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
import lxml.etree
import os
import re
import textwrap

from collections import namedtuple, OrderedDict
from datetime import date

from jinja2 import Environment, FileSystemLoader

from openerp import api, fields, models, tools
from openerp.tools.safe_eval import safe_eval

from . import licenses

_logger = logging.getLogger(__name__)

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
        default='9.0.1.0.0',
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

    workflow_ids = fields.Many2many(
        'workflow', 'prototype_wf_rel',
        'module_prototyper_id', 'workflow_id', 'Workflows',
        help=('Enter the list of workflow that you have created '
              'and want to export in this module')
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

    _env = None
    _data_files = ()
    _demo_files = ()
    _field_descriptions = None
    File_details = namedtuple('file_details', ['filename', 'filecontent'])
    template_path = '{}/../templates/'.format(os.path.dirname(__file__))

    @api.onchange('workflow_ids')
    def on_workflow_ids_change(self):
        act_ids = set(self.activity_ids._ids)
        for wf in self.workflow_ids:
            act_ids.update(set(wf.activities._ids))
        self.activity_ids = [(6, None, list(act_ids))]

    @api.onchange('activity_ids')
    def on_acitvity_ids_change(self):
        trans_ids = set(self.transition_ids._ids)
        for act in self.activity_ids:
            trans_ids.update(set(act.out_transitions._ids))
            trans_ids.update(set(act.in_transitions._ids))
        self.transition_ids = [(6, None, list(trans_ids))]

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
    def generate_files(self):
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
        file_details.extend(self.generate_data_files())
        file_details.extend(self.generate_workflow_files())
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

    @api.model
    def generate_data_files(self):
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
        for prefix, model_data, file_list in [
                ('data', data, self._data_files),
                ('demo', demo, self._demo_files)]:
            for model_name, records in model_data.iteritems():
                fname = self.friendly_name(self.unprefix(model_name))
                filename = '{0}/{1}.xml'.format(prefix, fname)
                self._data_files.append(filename)

                res.append(self.generate_file_details(
                    filename,
                    'data/model_name.xml.template',
                    model=model_name,
                    records=records,
                ))

        return res

    @api.model
    def _get_import_compat_fields_excluded(self, model_name):
        return ['create_uid', 'write_uid', 'create_date', 'write_date']

    @api.model
    def get_import_compat_fields(self, model_name):
        """Get the list fields in a format suited for the export_data function
        This method is inspired by
        openerp.addons.web.controllers.Export.get_fields
        """
        model = self.env[model_name]
        fields = model.fields_get()
        exclude = self._get_import_compat_fields_excluded(model_name)

        fields.pop('id', None)
        fields_sequence = sorted(
            fields.iteritems(),
            key=lambda field: tools.ustr(field[1].get('string', '')))

        records = []
        for field_name, field in fields_sequence:
            if exclude and field_name in exclude:
                continue
            if field.get('readonly'):
                # If none of the field's states unsets readonly, skip the field
                if all(dict(attrs).get('readonly', True)
                       for attrs in field.get('states', {}).values()):
                    continue
            if not field.get('exportable', True):
                continue

            id = field_name
            name = field['string']
            record = {'id': id, 'string': name,
                      'export_id': id, 'children': False,
                      'field_type': field.get('type'),
                      'required': field.get('required'),
                      'relation_field': field.get('relation_field'),
                      'selection': field.get('selection')}
            records.append(record)

            if len(name.split('/')) < 3 and 'relation' in field:
                ref = field.pop('relation')
                record['export_id'] += '/id'
                record['params'] = {'model': ref, 'prefix': id, 'name': name}

                if field['type'] == 'one2many':
                    # m2m field in import_compat is childless
                    record['children'] = True
        return records

    @api.model
    def _sanitize_value(self, field_value):
        """sanitaze value for xml export
        value is a dictionary item generated by get_import_compat_fields
        """
        value = field_value.get('value')
        field_type = field_value.get('field_type')
        if not value:
            return field_value
        if field_type in ('one2many', 'many2many'):
            value = [v.replace('__export__.', '') for v in value]
        elif field_type == 'many2one':
            value = value.replace('__export__.', '')
        elif field_type == 'selection':
            for key, val in field_value['selection']:
                if value == val:
                    value = key
                    break
        field_value['value'] = value
        return field_value

    @api.model
    def get_import_compat_values(self, model_instances):
        """For each instance this function build a list of dict. Each dict is
        the definition of the exported field (import compatible) with
        the corresponding value from the instance.
        The return value is a dict where key = model_instance, value = datas
        """
        ret = {}
        if len(model_instances) == 0:
            return ret
        model_name = model_instances._name
        # Here we get the definition of the fields that can be exported for
        # the given model. Only fields compatible for the import are retrieved
        fields_def = self.get_import_compat_fields(model_name)
        # The definition is a list of dict. We create a dict by 'export_id' of
        # these definitions. The export_id is the field's name to use to get
        # the value in a, import compatible way. Fox ex for relation fields,
        # the name = field_name/id
        fields_dict = dict(
            [(f['export_id'], f) for f in fields_def])
        fields_to_export = fields_dict.keys()
        multi_valued_field = [(f['export_id']) for f in fields_def if
                              f['field_type'] in ('one2many', 'many2many')]
        for instance in model_instances:
            datas = []
            # get exported data by using the same method as the one used
            # by the export wizard
            data_lines = instance.export_data(fields_to_export)['datas']
            values = instance.export_data(fields_to_export)['datas'][0]
            # values is a list of value in the same order as
            # the fields_to_export list. We now build a dictionary to safely
            # process these values
            values_dict = dict(zip(fields_to_export, values))
            # fix multi valued value:
            for key in multi_valued_field:
                value = values_dict[key]
                value = [value] if value else []
                values_dict[key] = value
            for line in data_lines[1:]:
                # multi valued fields are provided by additional lines
                line_values_dict = dict(zip(fields_to_export, line))
                for key in multi_valued_field:
                    val_item = line_values_dict[key]
                    if val_item:
                        values_dict[key].append(val_item)
            for export_id, value in values_dict.iteritems():
                # take a copy of the definition of the field.
                field_def = fields_dict[export_id].copy()
                # add the value retrieved on the instance
                field_def['value'] = value
                self._sanitize_value(field_def)
                datas.append(field_def)
            ret[instance] = datas
        return ret

    @api.multi
    def get_workflows_datas(self):
        """This methods return a list of model to export by wokflow. Each
        item is a list of models required to export the worklow
        Data is defined by the following structure
        [{ 'workflow': workflow,
           'xml_id': workflow xml_id,
          'data_models: {
              model_name1: [
                (model_instance, import compatible model values1),
                (model_instance, import compatible model values2),
                (model_instance, import compatible model valuesN])),
              model_name1: [
                (model_instance, import compatible model values1),
                (model_instance, import compatible model values2),
                (model_instance, import compatible model valuesN])),
          }}]
        The order in the data_models ordered_dict is the one used
        when rendering the xml record
        """
        self.ensure_one()
        workflows = {}
        datas = self.get_import_compat_values(self.workflow_ids)
        for wk, values in datas.iteritems():
            workflows.setdefault(
                wk, {'transitions': [], 'activities': [],
                     'values': values})

        datas = self.get_import_compat_values(self.transition_ids)
        for transition, values in datas.iteritems():
            wk_def = workflows.setdefault(
                transition.wkf_id, {'transitions': [], 'activities': []})
            wk_def['transitions'].append((transition, values))

        datas = self.get_import_compat_values(self.activity_ids)
        for activity, values in datas.iteritems():
            wk_def = workflows.setdefault(
                activity.wkf_id, {'transitions': [], 'activities': []})
            wk_def['activities'].append((activity, values))
        ret = []
        for workflow, val in workflows.iteritems():
            data_models = OrderedDict()
            if val.get('values'):
                # export workflow definition
                data_models['workflow'] = [(workflow, val['values'])]
            data_models['workflow.activity'] = val['activities']
            data_models['workflow.transition'] = val['transitions']
            ret.append({
                'workflow': workflow,
                'xml_id': self.get_model_xml_id(workflow),
                'data_models':  data_models
            })
        return ret

    @classmethod
    def get_model_xml_id(cls, model_instance):
        if not model_instance:
            return ''
        xml_id = model_instance.get_xml_id()
        return xml_id.values()[0].replace('__export__.', '')

    @classmethod
    def filter_field_values(cls, field_values, mode=None):
        """Return a list of field_values (items returned by
        get_import_compat_values) accooding to the given mode
        Possible value for mode:
        * None: return all values
        * no_relation: return all values for field with type not in
          (one2many, many2many)
        * relation_only: return all values for field with type in
          (one2many, many2many)
        """
        if not mode:
            return field_values
        if mode == 'no_relation':
            return [v for v in field_values if v['field_type'] not in (
                    'one2many', 'many2many')]
        if mode == 'relation_only':
            return [v for v in field_values if v['field_type'] in (
                    'one2many', 'many2many')]
        return field_values

    @api.multi
    def generate_workflow_files(self):
        """"Wrapper to generate the workflow definition files for the model.
        """
        self.ensure_one()
        workflows_def = []
        workflows = self.get_workflows_datas()
        for workflow_datas in workflows:
            xml_id = workflow_datas['xml_id']
            filepath = 'data/{}_workflow.xml'.format(
                self.friendly_name(self.unprefix(xml_id))
            )
            workflows_def.append(
                self.generate_file_details(
                    filepath,
                    'data/workflow_name.xml.template',
                    data=workflow_datas,
                    get_xml_id=self.get_model_xml_id,
                    filter_field_values=self.filter_field_values,
                )
            )
            self._data_files.append(filepath)

        return workflows_def

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
