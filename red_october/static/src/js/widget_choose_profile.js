/* Copyright 2016 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.WidgetChooseProfile', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Model = require('web.DataModel');

    /* It allows a user to choose their current encryption profile.

        Attributes:
            currentProfile (obj): This is the current profile that is being
                used for crypto.
            profiles (Set of obj): This represents all the profiles that the
                current user can access.
     */
    WidgetChooseProfile = Widget.extend({

        template: 'red_october.WidgetChooseProfile',

        /* It sets the widget properties */
        init: function (parent) {
            this._super(parent);
            this.profiles = new Set();
            this.currentProfile = {};
            this.currentPassword = '';
        },

        /* It overloads the start handler to call the data loader. */
        start: function () {
            this._super();
            this.loadData();
        },

        /* Load user profiles from the server, add them to the instance, then re-render. */
        loadData: function () {
            var RedOctoberUser = new Model('red.october.user');
            var self = this;
            RedOctoberUser.call('get_current_profile', []).then(function (profile) {
                self.loadProfile(profile, true);
            })
            RedOctoberUser.call('get_user_profiles', []).then(this.loadProfile);
            this.renderElement();
        },

        /* Load a single profile into the instance.

            Args:
                profile (obj): The RedOctoberUser profile to load.
                current (bool): True if this profile represents the current session profile.
         */
        loadProfile: function (profile, current) {
            this.profiles.add(profile);
            if (current) {
                this.currentProfile = profile;
            }
        }

        /* Render the dropdown and set click handler for the items. */
        renderElement: function () {
            this._super();
            if (this.profiles.length < 2) {
                this.$el.hide();
            } else {
                this.$el.show();
                this.$el.find('.ro-profile-select-item').click(self.selectProfile);
            }
        },

        /* This method is called when a profile select item is cicked. */
        clickProfile: function (event) {
            var profileID = $(event.currentTarget).data('profile-id');
            var self = this;
            if (profileID === self.currentProfileID) {
                return;
            }
            var uri = '/red_october/profile/change/' + profileID;
            return self.rpc(uri).done(function () {
                self.selectProfile(profileID);
            });
        },

        /* This method is called when a profile select item is cicked. */
        selectProfile: function (profileID) {
            var self = this;
            _.each(this.profiles, function (profile) {
                if (profile.id === profileID) {
                    self.currentProfile = profile;
                    self.currentPassword = '';
                };
            });
        },

    })

    return WidgetChooseProfile;

});
