openerp.testing.section('context_tunnel', {
    dependencies: ['web.list', 'web.form'],
    templates: true
}, function (test) {
    test("context composition", function (instance) {
        new openerp.web_context_tunnel(instance);
        var field_manager = new instance.web.form.DefaultFieldManager();
        var node = {'attrs': {'context': {'key1': 'value1', 'key2': 'value2'}, 'context_2': {'key3': 'value3'}, 'context_3': {'key4': 'value4'}}}
        var w = new instance.web.form.FormWidget(field_manager, node);
        var context = w.build_context().eval();
        ok(context['key1'] === 'value1', 'right value for key1 in context');
        ok(context['key2'] === 'value2', 'right value for key2 in context');
        ok(context['key3'] === 'value3', 'right value for key3 in context');
        ok(context['key4'] === 'value4', 'right value for key4 in context');
    });
});
