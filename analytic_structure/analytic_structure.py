# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 XCG Consulting (www.xcg-consulting.fr)
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

from openerp import exceptions
from openerp import fields, models, api
from openerp.tools import config
from openerp.tools.translate import _
import re
from lxml import etree
import json


class AnalyticStructure(models.Model):

    _name = 'analytic.structure'
    _description = u"Analytic Structure"

    def order_selection(self):
        order_selection = getattr(self, '_order_selection', None)
        if order_selection is None:
            size = int(config.get_misc('analytic', 'analytic_size', 5))
            order_selection = []
            for n in xrange(1, size + 1):
                order_selection.append((str(n), _(u"Analysis {}".format(n))))
            setattr(self, '_order_selection', order_selection)
        return order_selection

    @api.constrains('company_id', 'model_name', 'ordering')
    def _check_unique_ordering_no_company(self):
        columns = ['company_id', 'model_name', 'ordering']
        structures = self.read(columns)
        for structure in structures:
            if structure['company_id']:
                continue  # Already checked by the SQL constraint.
            domain = [
                ('model_name', '=', structure['model_name']),
                ('ordering', '=', structure['ordering']),
            ]
            count = self.search_count(domain)
            if count > 1:
                raise exceptions.ValidationError(
                    u"One dimension per Analysis slot per object when the"
                    u"structure is common to all companies."
                )

    model_name = fields.Char(
        u"Object",
        size=128,
        required=True,
        select='1',
    )
    nd_id = fields.Many2one(
        'analytic.dimension',
        u"Related Dimension",
        ondelete='restrict',
        required=True,
        select='1',
    )
    ordering = fields.Selection(
        order_selection,
        u"Analysis slot",
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        u"Company",
        default=lambda *a: False
    )

    _sql_constraints = [
        (
            'unique_ordering',
            'unique(company_id,model_name,ordering)',
            u"One dimension per Analysis slot per object per company."
        ),
    ]

    def format_field_name(self, ordering, prefix='a', suffix='id'):
        """Return an analytic field's name from its slot, prefix and suffix.
        """
        return '{pre}{n}_{suf}'.format(pre=prefix, n=ordering, suf=suffix)

    def extract_values(
        self, cr, uid, source, model, prefix='a', suffix='id', dest_model=None,
        dest_prefix=None, dest_suffix=None, context=None
    ):
        """For the given source and destination structures, defined by model,
        prefix and suffix, extract the values of all analytic fields from a
        source. Return the ID of those values, mapped with the field attributed
        to their dimension in the destination structure.

        Use this method to copy analytic data from an object to another.
        The source data can be a browse_record from browse or a dict from read.
        The return value is a dictionary. It can be directly passed as the vals
        or defaults attribute for the ORM methods create, write and copy.

        If not specified, the model, prefix and suffix for the destination
        fields are the same as those for the source fields.
        When a destination model is specified, only the values for dimensions
        present in both models will be returned (at their appropriate slot).
        """

        if dest_prefix is None:
            dest_prefix = prefix
        if dest_suffix is None:
            dest_suffix = suffix

        def add_field():
            src = self.format_field_name(slot, prefix, suffix)
            dest = self.format_field_name(dest_slot, dest_prefix, dest_suffix)
            if src in source:
                try:
                    res[dest] = source[src].id
                except AttributeError:
                    res[dest] = source[src]

        res = {}
        src_dim = self.get_dimensions(cr, uid, model, context=context)

        if dest_model is None or dest_model == model:
            for slot in src_dim.itervalues():
                dest_slot = slot
                add_field()

        else:
            dest_dim = self.get_dimensions(cr, uid, dest_model, context)
            for dimension, slot in src_dim.iteritems():
                if dimension in dest_dim:
                    dest_slot = dest_dim[dimension]
                    add_field()

        return res

    def get_structures(self, cr, uid, model, context=None):
        """Return the browse records of every analytic structure entry
        associated with the given model.
        """
        ans_ids = self.search(
            cr, uid,
            [('model_name', '=', model)],
            context=context
        )
        return self.browse(cr, uid, ans_ids, context=context)

    def get_dimensions(self, cr, uid, model, context=None):
        """Return a dictionary that contains the identifier (keys) and ordering
        number (values) of the analytic dimensions linked to the given model.
        """
        return {
            ans.nd_id.id: ans.ordering
            for ans in self.get_structures(cr, uid, model, context=context)
        }

    def get_dimensions_names(self, cr, uid, model, context=None):
        """Return a dictionary that contains the ordering numbers (keys) and
        names (values) of the analytic dimensions linked to the given model.
        """
        return {
            ans.ordering: ans.nd_id.name
            for ans in self.get_structures(cr, uid, model, context=context)
        }

    def analytic_fields_get(
        self, cr, uid, model, fields, prefix='a', suffix='id', context=None
    ):
        """Set the label values for the analytic fields."""

        ans_dict = self.get_dimensions_names(cr, uid, model, context=context)

        regex = r'{pre}(\d+)_{suf}'.format(pre=prefix, suf=suffix)
        match_fct = re.compile(regex).search
        matches = filter(None, map(match_fct, fields.keys()))

        for match in matches:
            field = match.group(0)
            slot = match.group(1)
            fields[field]['string'] = ans_dict.get(
                '{0}'.format(slot),
                '{0}{1}'.format(prefix.upper(), slot)
            )

        return fields

    def analytic_fields_subview_get(
        self, cr, uid, model, field, prefix='a', suffix='id', context=None
    ):
        """Apply analytic_fields_view_get to all subviews defined for a
        given relational field.
        The field argument is a field descriptor found inside the return value
        of fields_view_get. This method both updates and returns it:

        fvg_res = super(model_class, self).fields_view_get(...)
        field = fvg_res['fields'].get(field_name)
        analytic_fields_subview_get(cr, uid, 'analytic_model', field)
        # or...
        if field_name in fvg_res['fields']:
            fvg_res['fields'][field_name] = analytic_fields_subview_get(...)

        Avoid using subviews with analytic fields. It is better to define a new
        ir.ui.view record and pass it with the context key [type]_view_ref.
        """

        try:
            field_subviews = field['views']
        except:
            return field

        for view_mode, subview in field_subviews.iteritems():
            subview['model'] = field['relation']
            field_subviews[view_mode] = self.analytic_fields_view_get(
                cr, uid, model, subview, context=context
            )
        return field

    def analytic_fields_view_get(
        self, cr, uid, model, view, prefix='a', suffix='id', context=None
    ):
        """Show or hide used/unused analytic fields."""

        ans_dict = self.get_dimensions_names(cr, uid, model, context=context)
        found_fields = {slot: False for slot in ans_dict}

        regex = r'{pre}(\d+)_{suf}'.format(pre=prefix, suf=suffix)
        path = "//field[re:match(@name, '{0}')]".format(regex)
        ns = {"re": "http://exslt.org/regular-expressions"}

        doc = etree.XML(view['arch'])
        matches = doc.xpath(path, namespaces=ns)

        for match in matches:
            name = match.get('name')
            slot = re.search(regex, name).group(1)
            if slot in found_fields:
                # The analytic field is used and has been found in the view.
                found_fields[slot] = True
            else:
                # No analytic structure defined for this field, hide it.
                modifiers = json.loads(match.get('modifiers', '{}'))
                modifiers['invisible'] = modifiers['tree_invisible'] = True
                modifiers['required'] = False
                match.set('invisible', 'true')
                match.set('required', 'false')
                match.set('modifiers', json.dumps(modifiers))

        # Look for any field named 'analytic_dimensions' with the right prefix.
        name_cond = '@name="analytic_dimensions"'
        if prefix == 'a':
            pre_cond = '(@prefix="a" or not(@prefix))'
        else:
            pre_cond = '@prefix="{pre}"'.format(pre=prefix)
        if suffix == 'id':
            suf_cond = '(@suffix="id" or not(@suffix))'
        else:
            suf_cond = '@suffix="{suf}"'.format(suf=suffix)
        condition = '{0} and {1} and {2}'.format(name_cond, pre_cond, suf_cond)
        parent_matches = doc.xpath('//field[{cond}]/..'.format(cond=condition))

        if parent_matches:

            parent = parent_matches[0]
            elem = parent.xpath("//field[{cond}]".format(cond=condition))[0]
            for index, child in enumerate(parent):
                if child == elem:
                    break
            next_children = parent[index + 1:]
            del parent[index:]

            # Get all fields that are in the structure but not in the view.
            sorted_fields = found_fields.items()
            sorted_fields.sort(key=lambda i: int(i[0]))
            elem_fields = [
                self.format_field_name(ordering, prefix, suffix)
                for ordering, found in sorted_fields if not found
            ]

            # First, we have to load the definitions for those fields.
            if elem_fields:
                elem_fields_def = self.pool.get(view['model']).fields_get(
                    cr, uid, elem_fields, context=context
                )
                view['fields'].update(elem_fields_def)

                # Now we can insert the fields in the view's architecture.
                for field in elem_fields:
                    attrs = {'name': field}
                    modifiers = json.loads(elem.attrib.get('modifiers', '{}'))
                    attrs['modifiers'] = json.dumps({
                        attr: value for attr, value in modifiers.iteritems()
                        if attr != 'readonly' or
                        elem.attrib.get(attr, 'False') in ('True', 'true', '1')
                    })
                    for attr, value in elem.attrib.iteritems():
                        if attr in ['name', 'prefix', 'suffix', 'modifiers']:
                            continue
                        attrs[attr] = value
                    parent.append(etree.Element('field', attrs))

            parent.extend(next_children)

        view['arch'] = etree.tostring(doc)

        return view
