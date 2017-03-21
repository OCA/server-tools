/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.WidgetPasswordChange', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Model = require('web.DataModel');

    /* It allows a user to change their profile password.

        Attributes:
     */
    var WidgetPasswordChange = Widget.extend({

        template: 'red_october.WidgetPasswordChange',

        /* It sets the widget properties */
        init: function () {
            this._super(arguments);
        },

        /* It overloads the start handler to call the data loader. */
        start: function () {
            this._super();
            this.loadData();
        },

        /* Render the dropdown and set click handler for the items. */
        renderElement: function () {
            this._super();
            if (false && Object.keys(this.profiles).length < 2) {
                this.$el.hide();
            } else {
                this.$el.show();
            }
            this.setHandlers();
        },

    });

    return WidgetPasswordChange;

});
