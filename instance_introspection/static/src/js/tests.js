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
                waitFor: 'h3:contains("Addons Paths")',
                element: '.btn-reload',
                wait: 200,
            },
            {
                title:  'Load Repositories',
                waitFor: '#accordion.results',
            },
        ],
    });

})();

