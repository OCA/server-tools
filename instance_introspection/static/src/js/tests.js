(function() {
    'use strict';

    openerp.Tour.register({
        id: 'test_instance_introspection',
        name: 'Complete a basic order trough the Front-End',
        path: '/instance_introspection',
        mode: 'test',
        steps: [
            {
                title: 'Wait for the main screen',
                wait: 200,
            },
            {
                title:  'Load the Session',
                waitFor: '.list-group',
                element: 'h3:contains("Addons Path")',
            },
            {
                title:  'Load the List',
                waitFor: '.list-group-item',
                element: 'a:contains("Reload")',
            },
        ],
    });

})();

