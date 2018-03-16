openerp.base_optional_quick_create = function (instance){
	var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    instance.web.form.FieldMany2One.include({
		get_search_result : function(search_val) {
			var self = this;
			var result = this._super(search_val);
			var ir_model = new instance.web.DataSet(this, 'ir.model');
			var get_field_relation_model = function() {
			    return ir_model.call("search_read", [[['model', '=', self.field.relation]], ['avoid_quick_create',]]).then(function(models) {
                    model = models && models[0];
                    return model;
                })
			}
            return $.when(result, get_field_relation_model()).then(function(values, model){
                if (model.avoid_quick_create == true) {
                    var quick_create_string =  _.str.sprintf(_t('Create "<strong>%s</strong>"'), $('<span />').text(search_val).html());
                    return values.filter(function(item){return item.label !== quick_create_string});
                }
                return values;
            });
        }
	});
	instance.web.form.FieldMany2ManyTags.include({
	    get_search_result: function(search_val) {
			var self = this;
			var result = this._super(search_val);
			var ir_model = new instance.web.DataSet(this, 'ir.model');
			var get_field_relation_model = function() {
			    return ir_model.call("search_read", [[['model', '=', self.field.relation]], ['avoid_quick_create',]]).then(function(models) {
                    model = models && models[0];
                    return model;
                })
			}
            return $.when(result, get_field_relation_model()).then(function(values, model){
                if (model.avoid_quick_create == true) {
                    var quick_create_string =  _.str.sprintf(_t('Create "<strong>%s</strong>"'), $('<span />').text(search_val).html());
                    return values.filter(function(item){return item.label !== quick_create_string});
                }
                return values;
            });
        }
	});
}