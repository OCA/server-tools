openerp.profiler = function(instance) {
    openerp.profiler.profiler_enable(instance);
 };

openerp.profiler.profiler_enable = function(instance) {
    instance.profiler.controllers = {
        'profiler.enable': 'enable',
        'profiler.disable': 'disable',
        'profiler.clear': 'clear',
    };
    instance.profiler.simple_action = function(parent, action) {
        console.info(action);
        parent.session.rpc('/web/profiler/' + instance.profiler.controllers[action.tag], {});
    };

    instance.profiler.dump = function(parent, action) {
        $.blockUI();
        parent.session.get_file({
            url: '/web/profiler/dump',
            complete: $.unblockUI
        });

    };
    instance.web.client_actions.add("profiler.enable",
                                    "instance.profiler.simple_action");
    instance.web.client_actions.add("profiler.disable",
                                    "instance.profiler.simple_action");
    instance.web.client_actions.add("profiler.clear",
                                    "instance.profiler.simple_action");
    instance.web.client_actions.add("profiler.dump",
                                    "instance.profiler.dump");
};
