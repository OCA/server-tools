/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.WebClient', function (require) {
    "use strict";

    var core = require('web.core');
    var WebClient = require('web.WebClient');
    var WidgetProfileChoose = require('red_october.WidgetProfileChoose');

    WebClient.include({

        show_application: function() {
            this._super.apply(this, arguments);
            this.ro_choose_profile = new WidgetProfileChoose(this);
            var $user_menu = $('body').find('.o_user_menu');
            this.ro_choose_profile.insertBefore($user_menu);
        },

    })

    return {};

});
