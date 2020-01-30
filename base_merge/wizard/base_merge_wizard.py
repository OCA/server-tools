# -*- coding: utf-8 -*-
# © 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from lxml import etree
from odoo import _, api, fields, models


# this class is where the magic happens
class BaseMergeWizard(models.TransientModel):
    
    _name = 'base.merge.wizard'

    model_id = fields.Many2one(
      'ir.model',
      # the client sets the current model in the context, we need this later
      default=lambda self: self.env['ir.model'].search([
        ('name', '=', self.env.context.get('active_model'))]),
      readonly=True,
    )
    # we will make it look below as if this model has two fields like the following
    # target_id = fields.Many2one('the.model.mentioned.in.model_id')
    # source_ids = fields.Many2many('the.model.mentioned.in.model_id')
    # in order to hold the data for the above, we use base_sparse_field
    data = fields.Serialized()
  
    def fields_get(self, allfields=None, attributes=None):
      result = super(BaseMergeWizard, self).fields_get(
        allfields=allfields,
        attributes=attributes)
      return result
      if self.env.context:
          # make copies here otherwise we edit the original
          # dictionary, and we don't want that.
          active_model = self.env.context.get('active_model') or 'ir.model'
          copy_dict = result.get('model_id') or {}
          result['target_id'] = copy_dict.copy()
          result['target_id']['relation']  = active_model
          result['target_id']['type']  = 'many2one'
          result['target_id']['string']  = 'Target model'
          result['source_ids'] = copy_dict.copy()
          result['source_ids']['relation']  = active_model
          result['source_ids']['type'] = 'many2many'
          result['source_ids']['string'] = 'Target model records'
          import pdb; pdb.set_trace()
      return result

    def fields_view_get(self,
        view_id=None,
        view_type='form',
        toolbar=False,
        submenu=False):
        result = super(BaseMergeWizard, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu)
        return result
        if self.env.context.get('active_model') and result['fields'].get('model_id'):
            # make copies here otherwise we edit the original
            # dictionary, and we don't want that.
            result['fields']['target_id'] = result['fields']['model_id'].copy()
            result['fields']['target_id']['relation']  = self.env.context['active_model']
            result['fields']['target_id']['type']  = 'many2one'
            result['fields']['target_id']['string']  = 'Target model'
            result['fields']['source_ids'] = result['fields']['model_id'].copy()
            result['fields']['source_ids']['relation']  = self.env.context['active_model']
            result['fields']['source_ids']['type'] = 'many2many'
            result['fields']['source_ids']['string'] = 'Target model records'
            #  result['fields'].pop('data')
             # Edit view with these new fields, while keeping data there
            arch = etree.fromstring(result['arch'])
            placement_in_arch = arch.xpath("//field[@name='data']")
            if placement_in_arch:
                placement_in_arch = placement_in_arch[0]
                placement_in_arch.addnext(etree.Element('field', attrib=result['fields']['target_id']))
                placement_in_arch.addnext(etree.Element('field', attrib=result['fields']['source_ids']))
            result['arch'] = etree.tostring(arch)
            import pdb; pdb.set_trace()
        return result
      # inject your fields into arch. Define a formview with some placeholder in
      # data
    
    @api.model
    def create(self, vals):
        result = super(BaseMergeWizard, self).create(vals)
        # so what we do here and below, is to redirect writes to our virtual fields
        # into data, which we just make a dict of fieldnames->values. You'll have to
        # postprocess what you get from the many2one probably, in the end you just want
        # to save ids
        # vals[data] = {'target_id': vals.pop('target_id', None), etc}
        import pdb; pdb.set_trace()
        return result
    
    @api.multi
    def write(self, vals):
        result = super(BaseMergeWizard, self).write(vals)
        # so what we do here and below, is to redirect writes to our virtual fields
        # into data, which we just make a dict of fieldnames->values. You'll have to
        # postprocess what you get from the many2one probably, in the end you just want
        # to save ids
        # vals[data] = {'target_id': vals.pop('target_id', None), etc}
        return result
      
    def read(self):
      # and the inverse
      result = super()
      for record in result:
          record['target_id'] = record['data'].get('target_id')
          etc
      return result
  
    # this all we did to now to have a nice UI where the user sees the default
    # tree for their model, and we can use it conveniently in code
    def action_merge(self):
        return
      # self.data contains what we need, now sql magic comes
      # before doing so, check some group to make this safe
      
    def action_merge_and_next_duplicate(self):
        return
      # this will be called by the user during interactive deduplication
  
    def action_skip_and_next_duplicate(self):
        return
      # see above
