/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.DialogVaultNew', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var mixins = require('red_october.mixins');
    var Model = require('web.DataModel');

    var _t = core._t;

    /* It allows a user to get their profile password.

        Attributes:
     */
    var DialogVaultNew = Dialog.extend(
        mixins.dialogMixin,
        mixins.formMixin,
        {

            templateInner: 'red_october.FormVaultNew',

            options: {
                title: _t('Enter Vault Info'),
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

            handleSubmit: function (event) {

                event.preventDefault();

                var $target = $(event.target);
                var $parent = this.getParent();
                var arrData = $target.serializeArray();
                var objData = {};
                var Vaults = new Model('red.october.vault');

                _.each(arrData, function(data) {
                    objData[data.name] = data.value;
                })

                var vault = Vaults.call(
                    'create',
                    [{
                        'host': objData.host,
                        'port': objData.port,
                        'verify_cert': objData.verify_cert || false,
                    }]
                );
                vault.done(
                    this.proxy(function (record) {
                        $parent.$el.trigger(
                            'activateVault',
                            record,
                            objData.is_active
                        );
                    })
                );
                return vault;
            },

        }
    );

    return DialogVaultNew;

});
