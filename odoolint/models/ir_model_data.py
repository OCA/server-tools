# -*- coding: utf-8 -*-
# © 2016  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os

from openerp import api, fields, models, tools
from openerp.modules.module import get_module_resource

from ..hooks import get_file_info

_logger = logging.getLogger(__name__)


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    module_real = fields.Char(
        help="The `module` original field get the value from `module.xml_id`."
        "\nThis `module_real` field get the real module from module/ path."
    )
    section = fields.Char(
        size=8,
        help="Section of file from manifest file. E.g. (data, demo, test, ...)"
    )
    file_name = fields.Char(
        size=32,
        help="Record origin file name")
    table_name = fields.Char(
        size=64,
        help="Table name of database where is stored this record"
    )

    @api.model
    def create(self, values):
        """Inherit create for add custom values"""
        if values is None:
            values = {}
        new_values = get_file_info()
        model = values.get('model')
        if model:
            new_values['table_name'] = self.env[model]._table
        values.update(new_values)
        return super(IrModelData, self).create(values)

    @api.multi
    def _check_data_ref_demo(self):
        """Check data where a xml_id of section demo or test is referenced
        """
        self.ensure_one()
        imd_new = get_file_info()
        if self.section in ['demo', 'demo_xml', 'test'] and \
                imd_new.get('section') in ['data', 'init', 'update']:
            _logger.warning(
                "Demo xml_id '%s' of '%s/%s' is referenced "
                "from data xml '%s/%s'",
                self.name, self.module_real, self.file_name,
                imd_new['module_real'], imd_new['file_name'],
            )
            return False
        return True

    @api.multi
    def _check_xml_id_unachievable(self, xmlid):
        """Check a unachievable xml_id referenced
        """
        self.ensure_one()
        module = self.env['ir.module.module']
        imd_new = get_file_info()
        module_curr_str = imd_new.get('module_real')
        module_ref_str = xmlid.split('.')[0]
        if not module_curr_str or not module_ref_str or \
                module_ref_str == module_curr_str:
            return True
        module_curr = module.search([('name', '=', module_curr_str)], limit=1)
        module_curr_dep_ids = module_curr._get_module_upstream_dependencies(
            module_curr.ids, exclude_states=['uninstallable', 'to remove'])
        module_curr_deps = module.browse(module_curr_dep_ids).mapped('name')
        for mod_autinst in module.search([
                ('auto_install', '=', True),
                ('name', 'not in', module_curr_deps)]):
            mod_autinst_deps = mod_autinst.dependencies_id.mapped('name')
            if not mod_autinst_deps or \
                    set(mod_autinst_deps).issubset(set(module_curr_deps)):
                module_curr_deps.append(mod_autinst.name)

        if module_curr_deps and module_ref_str not in module_curr_deps:
            file_path = os.path.join(
                get_module_resource(imd_new['module_real']),
                imd_new['file_name'])
            file_content = open(file_path).read()
            if xmlid in file_content:
                # Many times a ref id is used from a default or inherit method
                # If the xml_id is in the content of the file, then is a real
                _logger.warning("The xml_id '%s' is unachievable.", xmlid)
                return False
        return True

    @tools.ormcache(skiparg=3)
    def xmlid_lookup(self, cr, uid, xmlid):
        res = super(IrModelData, self).xmlid_lookup(cr, uid, xmlid)
        self._check_data_ref_demo(cr, uid, res[0])
        self._check_xml_id_unachievable(cr, uid, res[0], xmlid)
        return res

    def _update(self, cr, uid, model, module, values, xml_id=False, store=True,
                noupdate=False, mode='init', res_id=False, context=None):
        """Inherit to force use of checks in case where a xml_id.record
        is overwrite from other module.
        """
        if module and xml_id and '.' in xml_id and \
                not xml_id.startswith(module + '.'):
            # Just in xml_id from other modules
            try:
                self.xmlid_lookup(cr, uid, xml_id)
            except BaseException:
                # All exceptions are off-target here
                pass
        return super(IrModelData, self)._update(
            cr, uid, model=model, module=module, values=values, xml_id=xml_id,
            store=store, noupdate=noupdate, mode=mode, res_id=res_id,
            context=context)
