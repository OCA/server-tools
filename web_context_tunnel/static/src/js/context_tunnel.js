openerp.web_context_tunnel = function(instance) {

    instance.web.form.FormWidget.prototype.build_context = function() {
        var v_context = false;
        var fields_values = false;
        // instead of using just the attr context, we merge any attr starting with context
        for (var key in this.node.attrs) {
            if (key.substring(0, 7) === "context") {
                if (!v_context) {
                    fields_values = this.field_manager.build_eval_context();
                    v_context = new instance.web.CompoundContext(this.node.attrs[key]).set_eval_context(fields_values);
                } else {
                    v_context = new instance.web.CompoundContext(this.node.attrs[key], v_context).set_eval_context(fields_values);
                }

            }
        }
        if (!v_context) {
            v_context = (this.field || {}).context || {};
            v_context = new instance.web.CompoundContext(v_context);
        }
        return v_context;
    };
};
