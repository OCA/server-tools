/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.WidgetProfileManage', function (require) {
    "use strict";

    var core = require('web.core');
    var web_client = require('web.web_client');

    var Widget = require('web.Widget');
    var Model = require('web.DataModel');

    var DialogPasswordChange = require('red_october.DialogPasswordChange');
    var DialogPasswordGet = require('red_october.DialogPasswordGet');
    var DialogVaultDelegate = require('red_october.DialogVaultDelegate');
    var DialogVaultNew = require('red_october.DialogVaultNew');

    var ERROR_PASSWORD = 'Wrong Password';

    /* It allows a user to choose their current encryption profile.

        Attributes:
            currentProfile (obj): This is the current profile that is being
                used for crypto.
            currentPassword (str): This is the password being used for login
                to currentProfile.
            profiles (Set of obj): This represents all the profiles that the
                current user can access.
     */
    var WidgetProfileManage = Widget.extend({

        template: 'red_october.WidgetProfileManage',

        events: {
            'decrypt': 'doDecrypt',
            'encrypt': 'doEncrypt',
            'decrementDelegation': 'decrementDelegation',
            'activateVault': 'activateVault',
        },

        /* It sets the widget properties */
        init: function (parent) {
            this._super(parent);
            this.profiles = {};
            this.vaults = {};
            this.delegations = {};
            this.currentProfile = {};
            this.currentPassword = '';
        },

        /* It overloads the start handler to call the data loader. */
        start: function () {
            this._super();
            this.loadData();
        },

        /* It sets the event handlers */
        setHandlers: function () {
            this.$el.find('a.roProfileSelect').click(
                this.proxy(this.clickProfile)
            );
            this.$el.find('#roProfilePasswordChange').click(
                this.proxy(this.clickProfilePasswordChange)
            );
            this.$el.find('#roProfilePasswordGet').click(
                this.proxy(this.clickProfilePasswordGet)
            );
            this.$el.find('#roVaultNew').click(
                this.proxy(this.clickVaultNew)
            );
        },

        /* Load user profiles from the server, add them to the instance, then re-render. */
        loadData: function () {
            var RedOctoberUser = new Model('red.october.user');
            var self = this;
            var loadProfileCurrent = function(records) {
                if (!records.length){
                    return;
                }
                self.loadProfile(records[0], true);
            }
            var loadProfiles = function(records) {
                self.loadProfiles(records);
            }
            RedOctoberUser.call('read_user_profiles').then(loadProfiles);
            RedOctoberUser.call('read_current_user').then(loadProfileCurrent);
        },

        /* Load multiple profiles into the instance.

            Args:
                profile (obj): The RedOctoberUser profile to load.
         */
        loadProfiles: function(profiles) {
            _.each(profiles, this.proxy(this.loadProfile));
            this.renderElement();
        },

        /* Load a single profile into the instance.

            Args:
                profile (obj): The RedOctoberUser profile to load.
                current (bool): True if this profile represents the current session profile.
         */
        loadProfile: function (profile, current) {
            this.profiles[profile.id] = profile;
            if (current) {
                this.selectProfile(profile.id);
            }
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

        /* This method is called when a profile select item is cicked. */
        clickProfile: function (event) {
            var profileID = $(event.currentTarget).data('profile-id');
            var self = this;
            if (profileID === this.currentProfileID) {
                return;
            }
            var uri = '/red_october/profile/change/' + profileID;
            return self.rpc(uri).done(function () {
                $.proxy(self.selectProfile, self, profileID);
            });
        },

        clickProfilePasswordChange: function (event) {
            new DialogPasswordChange(this).open();
        },

        clickProfilePasswordGet: function (event) {
            new DialogPasswordGet(this).open();
        },

        clickVaultNew: function (event) {
            new DialogVaultNew(this).open();
        },

        clickVaultDelegate: function (event) {
            var dialog = new DialogVaultDelegate(
                this,
                {
                    templateVals: {
                        vault: this.vaults[$(event.target).data('vault-id')],
                    },
                }
            );
            dialog.roVault = this.vaults[$(event.target).data('vault-id')];
            dialog.open();
        },

        /* It selects the profile given the ID */
        selectProfile: function (profileID) {
            _.each(
                this.profiles,
                $.proxy(function (profile) {
                    if (profile.id === profileID) {
                        this.$el.find('#roCurrentProfileName').text(profile.name);
                        this.currentProfile = profile;
                        this.currentPassword = '';
                    }
                }, this)
            );
            var vaults = new Model('red.october.vault').query(
                ['display_name', 'user_ids', 'delegation_ids']
            )
            vaults.filter([['id', 'in', this.currentProfile.vault_ids]]);
            vaults.all().then($.proxy(this.loadVaults, this));
            return vaults;
        },

        loadVaults: function (records) {
            var $header = this.$el.find('#roVaultDelegateHeader');
            _.each(
                records,
                $.proxy(function (record) {
                    this.vaults[record.id] = record;
                    var $li = $('<li class="text-center" />');
                    var $a = $(
                        '<a href="#" class="roVaultDelegate" data-vault-id="' + record.id + '"></a>'
                    );
                    $a.text(record.display_name);
                    $li.append($a);
                    $header.after($li);
                }, this)
            );
            this.$el.find('.roVaultDelegate').click(
                $.proxy(this.clickVaultDelegate, this)
            );
            var delegations = new Model('red.october.delegation').query(
                ['vault_id', 'user_id', 'date_expire', 'num_expire']
            )
            delegations.filter([['id', 'in', this.currentProfile.delegation_ids]]);
            delegations.all().then($.proxy(this.loadDelegations, this));
            return delegations;
        },

        activateVault: function (event, record, is_active) {
            var Wizards = new Model('red.october.vault.activate');
            Wizards.call(
                'create',
                [{
                    'is_active': is_active || false,
                    'vault_ids': [[(6, 0, [record])]],
                    'admin_user_id':
                }]
            )
        },

        upsertProfile: function (user, vaults) {
            var Users = new Model('red.october.user');
            Users.call(
                'create',
                [{

                }]
            )
        },

        loadDelegations: function(records) {
            _.each(
                records,
                $.proxy(function (record) {
                    this.delegations[record.id] = record;
                    var $delegateLink = this.$el.find('a[data-vault-id=' + record.vault_id[0] + ']');
                    $delegateLink.data('delegation-id', record.id);
                    this.updateDelegationText($delegateLink, record.num_expire);
                }, this)
            );
        },

        updateDelegationText: function($delegateLink, num_expire) {
            var delegation = this.delegations[$delegateLink.data('delegation-id')]
            var vault = this.vaults[delegation.vault_id[0]];
            delegation.num_expire = num_expire;
            $delegateLink.text(
                vault.display_name + ' (' + num_expire + ')'
            )
        },

        doEncrypt: function (event, field) {
            var self = this;
            var _encrypt = function () {
                self._crypt(field, 'encrypt').always(
                    $.proxy(self.handleCryptResponse, self, field, false)
                )
            };
            if (!this.currentPassword) {
                var dialog = new DialogPasswordGet(this);
                dialog.$modal.on('hidden.bs.modal', _encrypt);
                dialog.open();
            } else {
                _encrypt();
            }
        },

        doDecrypt: function (event, field) {
            var self = this;
            var _decrypt = function () {
                self._crypt(field, 'decrypt').always(
                    $.proxy(self.handleCryptResponse, self, field, true)
                )
            };
            if (!this.currentPassword) {
                var dialog = new DialogPasswordGet(this);
                dialog.$modal.on('hidden.bs.modal', _decrypt);
                dialog.open();
            } else {
                _decrypt();
            }
        },

        decrementDelegation: function (event, field) {
            var Delegations = new Model('red.october.delegation');
            var vaultID = field.currentAttachment.vault_id[0];
            var $delegateLink = this.$el.find('a[data-vault-id=' + vaultID + ']');
            var delegationID = $delegateLink.data('delegation-id');
            var num_expire = this.delegations[$delegateLink.data('delegation-id')].num_expire;
            this.updateDelegationText($delegateLink, num_expire - 1);
            Delegations.call(
                'decrement',
                [delegationID]
            );
        },

        handleCryptResponse: function (field, decrypted, response) {
            field.cryptAttempted = true;
            if (response.errors && response.errors.length) {
                _.each(response.errors, function(error) {
                    web_client.do_warn(error);
                });
            } else if (response.data) {
                field.handleCrypt(response.data, decrypted);
                if (decrypted) {
                    this.$el.trigger('decrementDelegation', field);
                }
                return;
            } else {
                web_client.do_warn('An unknown error occurred.');
            }
            if (field.cryptDefer) {
                field.cryptDefer.resolve(true);
            }
            field.render_value();
        },

        _crypt: function (field, method) {
            var uri = '/red_october/crypt/' + method;
            return $.ajax({
                method: 'POST',
                url: uri,
                data: {
                    data: field.get_value(),
                    password: this.currentPassword,
                    user_id: this.currentProfile.id,
                    csrf_token: odoo.csrf_token,
                },
                dataType: 'json',
            });
        }

    });

    return WidgetProfileManage;

});
