odoo.define('disable_odoo_online.announcement', function (require) {
	"use strict";
	var WebClient = require('web.WebClient');
	WebClient.include({
	    show_announcement_bar: function() {
	        // do nothing here
	    }
	});
});
