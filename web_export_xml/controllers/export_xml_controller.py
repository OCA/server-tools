# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Nikolina Todorova <nikolina.todorova@initos.com>
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
import simplejson
import operator
import copy
from openerp.addons.web import http as http
from openerp.addons.web.controllers.main import ExportFormat as ExportFormat
from openerp.addons.web.controllers.main import content_disposition
from xml.etree import ElementTree as ET
from cStringIO import StringIO as StringIO
from openerp.osv import orm
from openerp.osv.orm import fix_import_export_id_paths
from operator import itemgetter
from itertools import groupby

openerpweb = http


def create_2many_eval_str(ref_ids):
    """ Create string used afterwards for the eval parameter of field xml element.

    :param str ref_ids: the ids to which the field refers
    :return str used for the eval parameter
    """
    ref_ids.replace(" ", "")
    ref_list = ref_ids.split(',')
    eval_ref = []
    for ref in ref_list:
        eval_ref.append("ref('" + ref + "')")
    eval_ref = ",".join(eval_ref)
    eval_str = '[(6,0,[' + eval_ref + '])]'

    return eval_str


def create_date_eval_str(date):
    """ Create string used afterwards for the eval parameter of field xml element.

    :param str date: date/datetime string
    :return str used for the eval parameter
    """
    eval_str = "time.strftime('" + date + "')"

    return eval_str


# Compute xml data file help functions
def create_record_field(name, data=None, ref=None,
                        model=None, search=None, eval_str=None):
    """ Create field element

    :param str name: field name
    :param str data: field data
    :param str ref: field reference parameter
    :param str model: field model
    :param str search: field search parameter
    :param str eval_str: field eval parameter

    :return field: Tree field element
    :type field: ET.Element
    """
    field = ET.Element('field', {'name': name})
    if ref:
        field.set("ref", ref)
    if model:
        field.set("model", model)
    if search:
        field.set("search", search)
    if eval_str:
        field.set("eval", eval_str)
    if data:
        field.text = str(data)

    return field


def create_record(record_id, model, fields_list):
    """ Create record element.

    :param str record_id: record xml id
    :param str model: field model
    :param list fields_list: list of filed  elements type ET.Element


    :return record: Tree record element
    :type field: ET.Element
    """
    record = ET.Element('record', {'id': record_id, 'model': model})
    for val in fields_list:
        record.append(val)
    return record


def create_data_file(records_list):
    """ Create openerp element.

    :param list records_list: list of record elements type ET.Element

    :return openerp: Tree openerp element with all subelements
    :type openerp: ET.Element
    """
    openerp = ET.Element('openerp')
    data = ET.Element('data')
    openerp.append(data)

    for val in records_list:
        data.append(val)

    return openerp


# since the function is preceded with two underscores
# that is replaced with the model name
old___export_row = orm.BaseModel._BaseModel__export_row


def _BaseModel__export_row(self, cr, uid, row, fields,
                           context=None, import_compat=None):
    """ Extract the data that should be export for each record

    :param str row: row id
    :param list fields: fileds list of type str
    :param bool import_compat: are we exporting the ref fields or no

    :return
        if import_compat in [None, True]: old export function

        else: list result: List that contains lists for each field.
                           Fields list structure:
                               l[0] - record id
                               l[1] - model name
                               l[2] - field name
                               l[3] - field type. We handle 6 diff field types:
                                      'ref' - reference and m2o fields
                                      'normal' - integer, float, char, text,
                                                 binary, selection
                                      'many' - m2m, o2m
                                      'boolean' - boolean
                                      'date' - date, datetime
                                      'function' - function
                               l[4] - value
                               l[5] - required field
    """
    fields_to_export = copy.deepcopy(fields)
    if import_compat in [None, True]:
        return old___export_row(self, cr, uid, row, fields_to_export, context)
    else:
        def get_model(field):
            i = 0
            # for the first while iteration the model is the main object model
            model = self
            while i < len(field):
                if field[i] in model._inherit_fields.keys():
                    # [2] is the column obj of the inherited field
                    col = model._inherit_fields[field[i]][2]
                elif field[i] in model._columns.keys():
                    col = model._columns[field[i]]
                model = self.pool.get(col._obj)
                i += 1
            return model

        def get_field_type(model, field_name):
            """ Return the type of the field from the given model

            :param str model: model name
            :param str field_name: column name

            :return bool required
            """
            field_type = ''
            if field_name in model._columns.keys():
                field_type = model._columns[field_name]._type
            if isinstance(model._columns[field_name],
                          orm.fields.function) and \
                not isinstance(model._columns[field_name],
                               orm.fields.property):
                field_type = 'function'
            return field_type

        def get_required(model, field_name):
            """ Return if the field is required for the given model or not

            :param str model: model name
            :param str field_name: column name

            :return bool required
            """
            required = False
            if field_name in model._columns.keys():
                required = model._columns[field_name].required
            return required

        result = []
        # starts with the longest fields
        fields_to_export = sorted(fields_to_export, key=len, reverse=True)

        for group_len, field_groups in groupby(fields_to_export, len):
            for group in field_groups:
                field_value = ''
                field_type = ''
                field_model = ''
                field_id = ''
                while len(group) >= 1:
                    field_type = 'ref'
                    if not field_value:
                        all_values = old___export_row(self, cr, uid, row,
                                                      [group], context)
                        # we always use [0][0], because the function
                        # return always one list of lists.
                        # Where there is a inner list for
                        # each record (if the field is 2m).
                        # The last contains value for each field
                        # we can take [0][0], because the 2m fields
                        # are handled afterwards.
                        field_value = all_values[0][0]
                        field_type = 'normal'
                    field_name = group.pop()
                    model = get_model(group)
                    field_model = model._name
                    type = get_field_type(model, field_name)
                    if type in ['many2many', 'one2many']:
                        field_type = 'many'
                    if type == 'boolean':
                        field_type = 'boolean'
                    if type in ['date', 'datetime']:
                        field_type = 'date'
                    if type == 'function':
                        field_type = 'function'
                    required = get_required(model, field_name)
                    # add the id in order to get the id from the function
                    group.append('id')
                    all_f_ids = old___export_row(self, cr, uid, row,
                                                 [group], context)
                    field_id = all_f_ids[0][0]
                    # remove the id in order to proceed till the list is over
                    group.pop()
                    if field_id is False or field_name == 'id':
                        continue

                    if len(field_id.split(',')) > 1:
                        ids_vals = zip(field_id.split(','), all_values)
                        for id_val in ids_vals:
                            result.append([id_val[0], field_model,
                                           field_name, field_type,
                                           str(id_val[1][0]), required])
                    else:
                        result.append([field_id, field_model,
                                       field_name, field_type,
                                       str(field_value), required])

                    field_value = field_id
        return result
old_export_data = orm.BaseModel.export_data


def export_data(self, cr, uid, ids, fields_to_export,
                context=None, import_compat=None):
    """
    Export fields for selected objects

    :param cr: database cursor
    :param uid: current user id
    :param ids: list of ids
    :param fields_to_export: list of fields
    :param context: context arguments, like lang, time zone
    :param import_compat: are we exporting the ref fields or no
    :rtype: dictionary with a *datas* matrix

    This method is used when exporting data via client menu

    """
    if import_compat in [None, True]:
        return old_export_data(self, cr, uid, ids, fields_to_export, context)
    else:
        if context is None:
            context = {}
        if not context.get('lang'):
            res_user_model = self.pool.get('res.users')
            current_user = res_user_model.browse(cr, uid, uid,
                                                 context=context)
            lang = current_user.lang
            context.update({'lang': lang})

        # separate fields of type '.../...' to list ['','']
        fields_to_export = map(fix_import_export_id_paths, fields_to_export)
        datas = []
        # remove the 'id' field
        fields_to_export.pop(0)

        # prepare the records for export one by one
        for row in self.browse(cr, uid, ids, context):
            datas += self._BaseModel__export_row(cr, uid, row,
                                                 fields_to_export,
                                                 context, import_compat)
        return {'datas': datas}


orm.BaseModel.export_data = export_data
orm.BaseModel._BaseModel__export_row = _BaseModel__export_row


class ExportFormat(ExportFormat):

    @openerpweb.httprequest
    def index(self, req, data, token):
        if self.fmt['tag'] == 'xml':
            params = simplejson.loads(data)
            model, fields, ids, domain, import_compat = \
                operator.itemgetter('model', 'fields', 'ids', 'domain',
                                    'import_compat')(
                    params)

            Model = req.session.model(model)
            context = dict(req.context or {}, **params.get('context', {}))
            ids = ids or Model.search(domain, 0, False, False, context)

            field_names = map(operator.itemgetter('name'), fields)
            import_data = Model.export_data(ids, field_names, context,
                                            import_compat).get('datas', [])

            cont_disp = content_disposition(self.filename(model), req)
            return req.make_response(self.from_data(field_names,
                                                    import_data,
                                                    model,
                                                    import_compat),
                                     headers=[('Content-Disposition',
                                               cont_disp),
                                              ('Content-Type',
                                               self.content_type)],
                                     cookies={'fileToken': token})
        else:
            return super(ExportFormat, self).index(req, data, token)


class XMLExport(ExportFormat, http.Controller):
    _cp_path = '/web/export/xml'
    fmt = {'tag': 'xml', 'label': 'XML'}

    @property
    def content_type(self):
        """ Provides the format's content type """
        return 'text/xml;charset=utf8'

    def filename(self, base):
        """ Creates a valid filename for the format (with extension) from the
         provided base name (exension-less)
        """
        return base + '.xml'

    def from_data(self, fields, rows, model, import_compat):
        """ Conversion method from OpenERP's export data to the
        current export class outputs

        :params list fields: a list of fields to export
        :params list rows: a list of records to export
        :param model: model name
        :param import_compat - are we exporting the ref fields or no
        :returns:
        :rtype: bytes
        """
        fp = StringIO()
        record_list = []
        record_head_list = []  # List with all main records
        ref_ids_list = []
        fields.pop(0)  # remove external id

        if import_compat:
            for row in rows:
                ext_id = row.pop(0)  # remove external id
                fields_list = []
                for i in range(len(fields)):
                    fields_list.append(create_record_field(fields[i], row[i]))

                record_list.append(create_record(ext_id,
                                                 model,
                                                 fields_list))
        else:
            rows = [list(t) for t in set(map(tuple, rows))]
            rows = sorted(rows, key=itemgetter(0))
            for r_id, lists in groupby(rows, key=itemgetter(0)):
                fields_list = []
                fields_not_req_ref_list = []
                fields_not_req_many_list = []
                for l in lists:
                    ref = ''
                    ref_ids = ''  # used for adding fields to the ref_ids_list
                    eval_str = ''
                    data_value = ''
                    if l[3] == 'ref':
                        ref = l[4]
                        ref_ids = [l[4]]
                    elif l[3] == 'many':
                        if l[4] == "False":
                            continue
                        eval_str = create_2many_eval_str(l[4])
                        ref_ids = l[4].split(',')
                    elif l[3] == 'function':
                        continue
                    elif l[3] == 'boolean':
                        eval_str = l[4]
                    elif l[3] == 'date':
                        eval_str = create_date_eval_str(l[4])
                    else:
                        data_value = l[4]

                    # add the ref field only if it is required.
                    # That helps for ordering later.
                    if l[5] and ref_ids:
                        record_field = create_record_field(l[2],
                                                           data_value,
                                                           ref,
                                                           eval_str=eval_str)
                        fields_list.append(record_field)
                        for ref_id in ref_ids:
                            # create ref_id array used for ordering later
                            ref_ids_list.append(ref_id)
                    elif not l[5] and ref_ids:
                        record_field = create_record_field(l[2],
                                                           data_value,
                                                           ref,
                                                           eval_str=eval_str)
                        fields_not_req_ref_list.append(record_field)
                    else:
                        record_field = create_record_field(l[2],
                                                           data_value,
                                                           ref,
                                                           eval_str=eval_str)
                        fields_list.append(record_field)

                record_head_list.append(create_record(l[0], l[1], fields_list))
                if fields_not_req_ref_list:
                    for ls in fields_not_req_ref_list:
                        record_list.append(create_record(l[0], l[1], [ls]))
                if fields_not_req_many_list:
                    for ls in fields_not_req_many_list:
                        record_list.append(create_record(l[0], l[1], [ls]))

        def find_record_by_id(record_list, id):
            """
            Find the record element in the record list by its xml id

            :param list record_list - records from type ET.ELement
            :param str id: record xml id
            :return
                record - ET.ELement
                False - if no element was found
            """
            for record in record_list:
                criteria = ".[@id='"+ref_id+"']"
                el = record.findall(criteria)
                if el:
                    return record
            return False

        def find_records_that_refer_to_id(record_list, id):

            records = []
            indexes = []
            for record in record_list:
                criteria_1 = "./field/[@ref='"+ref_id+"']"
                criteria_2 = "./field/[@eval]"

                el_1 = record.findall(criteria_1)
                if el_1:
                    records.append(record)
                    indexes.append(record_list.index(record))

                el_2 = record.findall(criteria_2)
                for el in el_2:
                    if ref_id in el.get('eval'):
                        records.append(record)
                        indexes.append(record_list.index(record))
            return record_list[min(indexes)]

        not_sorted_flag = True
        while not_sorted_flag:
            not_sorted_flag = False
            for ref_id in ref_ids_list:
                reffered_element = find_record_by_id(record_head_list, ref_id)
                if not reffered_element:
                    continue
                refferer_element = \
                    find_records_that_refer_to_id(record_head_list, id)
                reffered_element_index = \
                    record_head_list.index(reffered_element)
                refferer_element_index = \
                    record_head_list.index(refferer_element)
                if reffered_element_index > refferer_element_index:
                    record_head_list.insert(refferer_element_index,
                                            reffered_element)
                    record_head_list.pop(reffered_element_index+1)
                    not_sorted_flag = True

        data_file_content = create_data_file(record_head_list + record_list)
        data = ET.tostring(data_file_content, encoding='utf8', method='xml')
        fp.write(data)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data
