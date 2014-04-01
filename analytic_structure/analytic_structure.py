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

from openerp.osv import fields, osv
import re
from lxml import etree
import json


ORDER_SELECTION = (
    ('1', 'Analysis 1'),
    ('2', 'Analysis 2'),
    ('3', 'Analysis 3'),
    ('4', 'Analysis 4'),
    ('5', 'Analysis 5')
)


class analytic_structure(osv.Model):

    _name = "analytic.structure"

    _columns = dict(
        model_name=fields.char("Object", size=128, required=True, select="1"),
        nd_id=fields.many2one(
            "analytic.dimension",
            "Related Dimension",
            ondelete="restrict",
            required=True,
            select="1"
        ),
        ordering=fields.selection(
            ORDER_SELECTION,
            'Analysis slot',
            required=True),
    )
    _sql_constraints = [
        (
            'unique_ordering',
            'unique(model_name,ordering)',
            'One dimension per Analysis slot per object'
        ),
    ]

    def _get_dimensions_names(self, cr, uid, model, context=None):
        """Get the names of the analysis dimensions linked to a given model."""

        ans_ids = self.search(
            cr, uid,
            [('model_name', '=', model)],
            context=context
        )
        ans_brs = self.browse(cr, uid, ans_ids, context=context)

        return {
            ans.ordering: ans.nd_id.name
            for ans in ans_brs
        }

    def analytic_fields_get(
        self, cr, uid, model, fields, prefix='a', context=None
    ):
        """Set the label values for the analytic fields."""

        ans_dict = self._get_dimensions_names(cr, uid, model, context=context)

        regex = '{0}(\d+)_id'.format(prefix)
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

    def analytic_fields_view_get(
        self, cr, uid, model, view, prefix='a', context=None
    ):
        """Show or hide used/unused analytic fields."""

        ans_dict = self._get_dimensions_names(cr, uid, model, context=context)

        regex = '{0}(\d+)_id'.format(prefix)
        path = "//field[re:match(@name, '{0}')]".format(regex)
        ns = {"re": "http://exslt.org/regular-expressions"}

        doc = etree.XML(view['arch'])
        matches = doc.xpath(path, namespaces=ns)

        for match in matches:
            name = match.get('name')
            slot = re.search(regex, name).group(1)
            is_invisible = not slot in ans_dict
            modifiers = json.loads(match.get('modifiers', '{}'))
            modifiers['invisible'] = modifiers['tree_invisible'] = is_invisible
            match.set('modifiers', json.dumps(modifiers))

        view['arch'] = etree.tostring(doc)
        return view
