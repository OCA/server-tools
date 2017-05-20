from openerp.osv import orm, fields
from openerp.tools.translate import _


class BaseActionRule(orm.Model):
    _inherit = 'base.action.rule'

    _columns = {
        'act_add_tag_ids': fields.many2many('res.tag', 'base_action_rule_add_tag_ids_rel', 'rule_id', 'tag_id',
                                            string="Add Tags", select=True,
                                            help="Specify tags to be added to object this rule is applied to"),
        'act_remove_tag_ids': fields.many2many('res.tag', 'base_action_rule_remove_tag_ids_rel', 'rule_id', 'tag_id',
                                               string="Remove Tags", select=True,
                                               help="Specify tags to be removed from object this rule is applied to"),
    }

    # Overridden to add tag related logic
    def _process(self, cr, uid, action, record_ids, context=None):
        """ process the given action on the records """
        super(BaseActionRule, self)._process(cr, uid, action, record_ids, context=context)

        model = self.pool.get(action.model_id.model)
        if action.act_add_tag_ids and model.fields_get(cr, uid, ['tag_ids']).get('tag_ids', False):
            tag_ids_val = [(4, int(t)) for t in action.act_add_tag_ids]
            model.write(cr, uid, record_ids, {'tag_ids': tag_ids_val}, context=context)

        if action.act_remove_tag_ids and model.fields_get(cr, uid, ['tag_ids']).get('tag_ids', False):
            tag_ids_val = [(3, int(t)) for t in action.act_remove_tag_ids]
            model.write(cr, uid, record_ids, {'tag_ids': tag_ids_val}, context=context)
