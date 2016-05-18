odoo.define('auth_signup_verify_email.tour_register_with_email', function (require) {
	'use strict';
	var core = require('web.core');
	var Tour = require('web.Tour');
	var _t = core._t;

	Tour.register({
		id: 'register_with_email',
		name: _t('Register with email'),
		path: '/web/signup',
		mode: 'test',
		steps: [
			{
				title: 'Input email',
				element: 'input[name="login"][value="john@got.com"]',
				sampleText:'john@got.com',
			},
			{
				title: 'Input name',
				element: 'input[name="name"][value="John Snow"]',
				sampleText:'John Snow',
			},
			{
				title: 'Click Sign up button',
				element: 'button.btn.btn-primary.pull-left',
			},
		],
	});
};