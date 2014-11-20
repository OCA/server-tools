# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

""" procedural code is executed even if the module is not installed

 TRY TO SWITCH to _register_hook() in the model to avoid
 execution when not installed in V 8.0 version

"""

from openerp.osv import orm
from lxml import etree
import os


module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

DUMMY_MODEL = 'module.%s.installed' % module_name.replace('_', '.')


class DummyModel(orm.Model):
    """ Allow to check if module is installed or not
        in fields_view_get method to avoid code execution if not
        Only executed if the module is installed
    """
    _name = DUMMY_MODEL


fields_view_get_orginal = orm.BaseModel.fields_view_get


def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                    context=None, toolbar=False, submenu=False):
    res = fields_view_get_orginal(
        self, cr, uid, view_id=view_id, view_type=view_type, context=context,
        toolbar=toolbar, submenu=submenu)
    if view_type == 'tree':
        compatible_tree = res.get('field_parent', True) is False
        # Tree views with res['field_parent'] different from False
        # looks like 'Products by Category'.
        # We don't modify these views
        # to avoid to break them (js error)
        if '_transient_max_count' in self.pool[res['model']].__dict__.keys():
            # model with '_transient_max_count' key are transient model
            # transient models haven't 'id' column in mostly case
            compatible_tree = False
        if compatible_tree and DUMMY_MODEL in self.pool.models.keys():
            doc = etree.XML(res['arch'])
            if (doc.xpath("//tree") and
                    len(doc.xpath("//field[@name='id']"))) == 0:
                node = doc.xpath("//tree")[0]
                node.append(etree.Element("field", name="id", string="Id"))
                res['arch'] = etree.tostring(node)
    return res


orm.BaseModel.fields_view_get = fields_view_get
