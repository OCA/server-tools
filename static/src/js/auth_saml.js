openerp.auth_saml = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.Login.include({
        start: function(parent, params) {
            var self = this;
            var d = this._super.apply(this, arguments);
            this.$el.hide();
            this.$el.on('click', 'a.zocial', this.on_saml_sign_in);
            this.saml_providers = [];
            if(this.params.saml_error === 1) {
                this.do_warn(_t("Sign up error"),_t("Sign up is not allowed on this database."), true);
            } else if(this.params.saml_error === 2) {
                this.do_warn(_t("Authentication error"),_t("Access Denied"), true);
            } else if(this.params.saml_error === 3) {
                this.do_warn(_t("Authentication error"),_t("You do not have access to this database or your invitation has expired. Please ask for an invitation and be sure to follow the link in your invitation email."), true);
            }
            return d.done(this.do_saml_load).fail(function() {
                self.do_saml_load([]);
            });
        },
        on_db_loaded: function(result) {
            this._super.apply(this, arguments);
            this.$("form [name=db]").change(this.do_saml_load);
        },
        do_saml_load: function() {
            var db = this.$("form [name=db]").val();
            if (db) {
                this.rpc("/auth_saml/list_providers", { dbname: db }).done(this.on_saml_loaded);
            } else {
                this.$el.show();
            }
        },
        on_saml_loaded: function(result) {
            this.saml_providers = result;
            var params = $.deparam($.param.querystring());
            if (this.saml_providers.length === 1 && params.type === 'signup') {
                this.do_saml_sign_in(this.saml_providers[0]);
            } else {
                this.$el.show();
                this.$('.oe_saml_provider_login_button').remove();
                var buttons = QWeb.render("auth_saml.Login.button",{"widget":this});
                this.$(".oe_login_pane form ul").after(buttons);
            }
        },
        on_saml_sign_in: function(ev) {
            ev.preventDefault();
            var index = $(ev.target).data('index');
            var provider = this.saml_providers[index];
            return this.do_saml_sign_in(provider);
        },
        do_saml_sign_in: function(provider) {
            var state = this._saml_state(provider);
            this.rpc("/auth_saml/get_auth_request", { relaystate: JSON.stringify(state) }).done(this.on_request_loaded);
        },
        on_request_loaded: function(result) {
            // redirect to the saml idp
            //instance.web.redirect(result.auth_request);
            window.location.replace(result.auth_request);
        },
        _saml_state: function(provider) {
            // return the state object sent back with the redirected uri
            var dbname = this.$("form [name=db]").val();
            return {
                d: dbname,
                p: provider.id,
            };
        },
    });

};
