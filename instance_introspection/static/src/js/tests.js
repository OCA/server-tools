(function() {
    'use strict';

    openerp.Tour.register({
        id: 'test_instance_introspection',
        name: 'Complete a basic order trough the Front-End',
        path: '/instance_introspection',
        mode: 'test',
        steps: [
            {
                title:   'Wait fot the bloody screen to be ready',
                wait: 200,
            },
            {
                title:  'Load the Session',
                waitNot: '.jumbotron',
                element: 'h1:contains("Branch Information")',
            },
        ],
    });

})();

