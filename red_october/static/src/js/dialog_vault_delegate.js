/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.DialogVaultDelegate', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var mixins = require('red_october.mixins');
    var Model = require('web.DataModel');

    var _t = core._t;

    /* It allows a user to get their profile password.

        Attributes:
     */
    var DialogVaultDelegate = Dialog.extend(
        mixins.dialogMixin,
        mixins.formMixin,
        {

            templateInner: 'red_october.FormVaultDelegate',

            options: {
                title: _t('Enter Delegation Info'),
                buttons: [
                    {
                        text: _t('Submit'),
                        classes: 'btn btn-primary',
                        close: true,
                        click: function(event){
                            this.$form.submit();
                        },
                    },
                    {
                        text: _t('Cancel'),
                        classes: 'btn btn-default',
                        close: true,
                        click: function () {
                            this.resetUI();
                        }
                    },
                ],
            },

        }
    );

    return DialogVaultDelegate;

});
