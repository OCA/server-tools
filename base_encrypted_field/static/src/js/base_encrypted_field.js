//-*- coding: utf-8 -*-
//© 2016 Therp BV <http://therp.nl>
//License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

openerp.base_encrypted_field = function(instance)
{
    instance.base_encrypted_field.get_pgp_keys = function(widget)
    {
        if(!widget.session.user_pgp_private_key)
        {
            return new instance.web.DataSet(widget, 'res.users')
            .read_ids([widget.session.uid], ['pgp_private_key', 'pgp_public_key'])
            .then(function(values)
            {
                values = values[0];
                if(values.pgp_private_key && values.pgp_public_key)
                {
                    var private_key = openpgp.key.readArmored(
                            values.pgp_private_key),
                        public_key = openpgp.key.readArmored(
                            values.pgp_public_key);
                    if(private_key.err || public_key.err)
                    {
                        throw new SyntaxError(
                            instance.web._t('Your keypair is invalid. Please regenerate it via your user settings')
                        )
                    }
                    widget.session.user_pgp_private_key = private_key.keys[0];
                    widget.session.user_pgp_public_key = public_key.keys[0];
                    return instance.base_encrypted_field.get_pgp_keys(widget);
                }
                else
                {
                    return instance.base_encrypted_field.update_pgp_keys(widget, widget.session.uid)
                    .then(function()
                    {
                        return instance.base_encrypted_field.get_pgp_keys(widget);
                    })
                }
            })
        }
        else
        {
            var deferred = new jQuery.Deferred();
            if(!widget.session.user_pgp_private_key.getEncryptionKeyPacket().isDecrypted)
            {
                widget.rpc(
                    '/web/action/load',
                    {action_id: 'base_encrypted_field.action_base_encrypted_field_get_passphrase'})
                .done(function(action)
                {
                    on_close = function()
                    {
                        if(!widget.session.user_pgp_private_key.getEncryptionKeyPacket().isDecrypted)
                        {
                            deferred.reject();
                        }
                    }
                    widget.do_action(action, {on_close: on_close}).then(function()
                    {
                        widget.field_manager.ViewManager.ActionManager.dialog_widget.dataset.on(
                            'dataset_changed', self, function(data)
                            {
                                if(data.passphrase)
                                {
                                    widget.session.user_pgp_private_key.decrypt(data.passphrase);
                                    if(!widget.session.user_pgp_private_key.getEncryptionKeyPacket().isDecrypted)
                                    {
                                        deferred.reject()
                                    }
                                    else
                                    {
                                        deferred.resolve(widget.session.user_pgp_private_key, widget.session.user_pgp_public_key);
                                    }
                                }
                            });
                    });
                })
            }
            else
            {
                deferred.resolve(widget.session.user_pgp_private_key, widget.session.user_pgp_public_key);
            }
            return deferred.promise();
        }
    }
    instance.base_encrypted_field.update_pgp_keys = function(widget, user_id)
    {
        if(!widget)
        {
            // we're call on a user form, find it and assign widget, user_id
            var find_pgp_widget = function(widget, form)
            {
                if(widget.field_manager && widget.field_manager.dataset &&
                   widget.field_manager.dataset.model == 'res.users' &&
                   widget.name == 'pgp_private_key')
                {
                    return widget;
                }
                if(widget.getChildren)
                {
                    var children = widget.getChildren();
                    for(var i=0; i < children.length; i += 1)
                    {
                        var found = find_pgp_widget(children[i], form);
                        if(found && found != form)
                        {
                            return found;
                        }
                    }
                }
                return form;
            }
            widget = find_pgp_widget(instance.webclient);
            user_id = widget.field_manager.dataset.ids[widget.field_manager.dataset.index];
        }
        return widget.rpc(
            '/web/action/load',
            {action_id: 'base_encrypted_field.action_base_encrypted_field_update_key'})
        .done(function(action)
        {
            var create_key_deferred = new jQuery.Deferred(),
            on_close = function()
            {
                if(widget.session.user_pgp_private_key)
                {
                    create_key_deferred.resolve(
                        widget.session.user_pgp_private_key,
                        widget.session.user_pgp_public_key);
                }
            }
            action.context = {}
            action.context.default_user_id = user_id;
            widget.do_action(action, {on_close: on_close}).then(function()
            {
                var res_users = new instance.web.DataSet(widget, 'res.users');
                widget.field_manager.ViewManager.ActionManager.dialog_widget.dataset.on(
                    'dataset_changed', self, function(data)
                    {
                        //TODO: save old keypair to recode afterwards
                        if(data.passphrase && !data.private_key)
                        {
                            return res_users.read_ids([data.user_id], ['name', 'email'])
                            .then(function(values)
                            {
                                values = values[0];
                                var options = {
                                    numBits: 4096,
                                    userIds: [
                                        _.str.sprintf(
                                            '%s <%s>',
                                            values.name, values.email),
                                    ],
                                    passphrase: data.passphrase,
                                };
                                instance.web.blockUI();
                                return openpgp.generateKey(options)
                                .then(function(keypair)
                                {
                                    widget.session.user_pgp_private_key = keypair.key;
                                    widget.session.user_pgp_public_key = keypair.key.toPublic();
                                    widget.session.user_pgp_private_key.decrypt(data.passphrase);
                                    create_key_deferred.resolve(
                                        widget.session.user_pgp_private_key,
                                        widget.session.user_pgp_public_key);
                                    return res_users.write(
                                        data.user_id,
                                        {
                                            pgp_public_key: keypair.publicKeyArmored,
                                            pgp_private_key: keypair.privateKeyArmored,
                                        })
                                    .then(function()
                                    {
                                        instance.web.unblockUI();
                                    });
                                });
                            })
                        }
                        else if(data.private_key)
                        {
                            if(data.passphrase && !data.public_key)
                            {
                                var private_key = openpgp.key.readArmored(
                                    data.private_key)
                                if(private_key.err)
                                {
                                    throw new SyntaxError(
                                        instance.web._t('Your private key is invalid'));
                                }
                                private_key = private_key.keys[0]
                                private_key.decrypt(data.passphrase);
                                if(!private_key.getEncryptionKeyPacket().isDecrypted)
                                {
                                    throw new SyntaxError(
                                        instance.web._t('Your passphrase is invalid'));
                                }
                                data.public_key = private_key.toPublic().armor();
                            }
                            if(data.user_id == widget.session.uid)
                            {
                                var private_key = openpgp.key.readArmored(
                                    data.private_key),
                                    public_key = openpgp.key.readArmored(
                                        data.public_key);
                                if(private_key.err || public_key.err)
                                {
                                    throw new SyntaxError(
                                        instance.web._t('Your keypair is invalid'));
                                }
                                widget.session.user_pgp_private_key = private_key.keys[0];
                                widget.session.user_pgp_public_key = public_key.keys[0];
                                if(data.passphrase)
                                {
                                    widget.session.user_pgp_private_key.decrypt(data.passphrase);
                                }
                            }
                            return res_users.write(
                                data.user_id,
                                {
                                    pgp_public_key: data.public_key,
                                    pgp_private_key: data.private_key,
                                });
                        }
                    });
            });
            return create_key_deferred.promise();
        })
    }
    instance.base_encrypted_field.select_or_create_group = function(widget, private_key, public_key)
    {
        var self = this,
            get_group_deferred = new jQuery.Deferred();
        widget.rpc(
            '/web/action/load',
            {action_id: 'base_encrypted_field.action_base_encrypted_field_select_or_create_group'})
        .done(function(action)
        {
            var encryption_group_id = null, additional_user_ids = [],
            on_close = function()
            {
                if(encryption_group_id)
                {
                    debugger;
                }
            }
            return widget.do_action(action, {on_close: on_close}).then(function()
            {
                widget.field_manager.ViewManager.ActionManager.dialog_widget.dataset.on(
                    'dataset_changed', self, function(data)
                {
                    if(data.encryption_group_id)
                    {
                        encryption_group_id = data.encryption_group_id;
                    }
                    else if(data.new_name)
                    {
                        // TODO: is this enough?
                        instance.web.blockUI();
                        var passphrase = openpgp.crypto.random.getRandomBytes(16);
                        return openpgp.encrypt({
                            data: passphrase,
                            publicKeys: public_key,
                            privateKeys: private_key,
                            armor: true,
                        })
                        .then(function(encrypted)
                        {
                            // TODO: also create encrypted.field records for
                            // additional_user_ids
                            var encrypted_field_user_ids = [
                                [0, 0, {
                                    user_id: widget.session.uid,
                                    key: encrypted.data,
                                }],
                            ];
                            return new instance.web.Model('encryption.group').call(
                                'create', [{
                                    name: data.new_name,
                                    encrypted_field_user_ids: encrypted_field_user_ids,
                                }])
                            .then(function(group_id)
                            {
                                encryption_group_id = group_id;
                                additional_user_ids = data.new_member_ids[0][2];
                                widget.field_manager.set_encryption_parameters(
                                    widget, passphrase, group_id,
                                    encrypted.data);
                                widget._dirty_flag = true;
                                instance.web.unblockUI();
                                return true;
                            });
                        })
                    }
                });
            });
        });
        return get_group_deferred.promise();
     }
    instance.web.FormView.include({
        init: function()
        {
            this.encryptable_fields = {}
            return this._super.apply(this, arguments);
        },
        register_field: function(field, name)
        {
            if(field.field.encryptable)
            {
                this.encryptable_fields[name] = field;
            }
            return this._super.apply(this, arguments);
        },
        is_field_encryptable: function(field)
        {
            return this.encryptable_fields[field.name];
        },
        is_field_encrypted: function(field)
        {
            return !!this.get_encryption_parameters(field);
        },
        set_encryption_parameters(
            field, passphrase, group_id, encrypted_passphrase, record
        )
        {
            (record || this.datarecord)[
                _.str.sprintf('%s.encrypted', field.name)
            ] = {
                passphrase: passphrase,
                group_id: group_id,
                encrypted_passphrase: encrypted_passphrase,
            };
        },
        get_encryption_parameters(field)
        {
            return this.datarecord[
                _.str.sprintf('%s.encrypted', field.name)
            ];
        },
        _process_save: function(save_obj)
        {
            var self = this,
                _super = self._super,
                deferreds = [];
            _.each(this.encryptable_fields, function(field)
            {
                var parameters = self.get_encryption_parameters(field),
                    deferred = new jQuery.Deferred();
                if(!parameters)
                {
                    return;
                }
                field.set('value.unencrypted', field.get_value());
                deferreds.push(deferred);
                triplesec.encrypt(
                    {
                        data: new triplesec.Buffer(field.get_value()),
                        key: new triplesec.Buffer(parameters.passphrase),
                    },
                    function(error, buffer)
                    {
                        if(error)
                        {
                            // TODO: do something
                            return;
                        }
                        field._inhibit_on_change_flag = true;
                        field.internal_set_value(buffer.toString('base64'));
                        field._inhibit_on_change_flag = false;
                        deferred.resolve()
                    }
                );
            });
            return jQuery.when.apply(jQuery, deferreds).then(function()
            {
                return _super.apply(self, [save_obj])
                .then(function(result)
                {
                    var encrypted_fields = []
                    _.each(self.encryptable_fields, function(field)
                    {
                        var parameters = self.get_encryption_parameters(field);
                        if(!parameters)
                        {
                            return;
                        }
                        encrypted_fields.push({
                            group_id: parameters.group_id,
                            res_model: self.model,
                            res_id: self.datarecord.id,
                            field: field.name,
                        });
                        field._inhibit_on_change_flag = true;
                        field.internal_set_value(
                            field.get('value.unencrypted'));
                        delete field.__getterSetterInternalMap[
                            'value.unencrypted'
                        ];
                        field._inhibit_on_change_flag = false;
                    });
                    if(!encrypted_fields.length)
                    {
                        return result;
                    }
                    return new instance.web.Model('encryption.group')
                    .call('update_encrypted_fields', [encrypted_fields])
                    .then(function()
                    {
                        return result;
                    });
                });
            });
        },
        load_record: function(record)
        {
            var self = this,
                _super = this._super,
                deferred = false;
            if(!_.isEmpty(self.encryptable_fields))
            {
                // TODO: can we inject that into read somehow?
                deferred = new instance.web.Model('encryption.group')
                .call('get_encrypted_fields', [self.model, record.id])
                .then(function(encrypted_fields)
                {
                    _.each(encrypted_fields, function(encrypted_field)
                    {
                        self.set_encryption_parameters(
                            self.fields[encrypted_field.field], false,
                            encrypted_field.group_id,
                            encrypted_field.encrypted_passphrase, record);
                    });
                });
            }
            return jQuery.when(deferred).then(function()
            {
                return _super.apply(self, [record])
                .then(function(result)
                {
                    if(_.isEmpty(self.encryptable_fields))
                    {
                        return result;
                    }
                    // TODO: this should happen in setValue, we need overrides
                    // specific to the fields in question to make this work
                    _.each(self.fields, function(field)
                    {
                        if(field.field.encryptable)
                        {
                            field.update_encrypted_field_commands();
                        }
                    });
                    return result
                });
            });
        },
    });
    instance.web.form.AbstractField.include({
        renderElement: function()
        {
            var result = this._super.apply(this, arguments);
            this.update_encrypted_field_commands();
            return result;
        },
        update_encrypted_field_commands: function()
        {
            var $containers = this.$el.add(this.$label);
            if(this.field_manager.is_field_encryptable &&
                this.field_manager.is_field_encryptable(this))
            {
                if(this.field_manager.is_field_encrypted(this))
                {
                    this.$el.addClass('oe_form_field_encrypted');
                    $containers.find('.oe_field_decrypt').click(
                        this.proxy('on_decrypt'));
                    $containers.find('.oe_field_encrypt').hide();
                    $containers.find('.oe_field_decrypt').show();
                }
                else
                {
                    $containers.find('.oe_field_encrypt').click(
                        this.proxy('on_encrypt'));
                    $containers.find('.oe_field_decrypt').hide();
                    $containers.find('.oe_field_encrypt').show();
                }
            }
            else
            {
                $containers.find('.base_encrypted_field_commands').remove();
            }
        },
        on_encrypt: function()
        {
            var self = this;
            return instance.base_encrypted_field.get_pgp_keys(this)
            .then(function(private_key, public_key)
            {
                return instance.base_encrypted_field.select_or_create_group(
                    self, private_key, public_key)
            });
        },
        on_decrypt: function()
        {
            var self = this;
            return instance.base_encrypted_field.get_pgp_keys(this)
            .then(function(private_key, public_key)
            {
                var encryption_parameters = self.field_manager
                        .get_encryption_parameters(self),
                    // HTML fields wrap the value in a p tag
                    value = jQuery(self.get_value()).text();
                return openpgp.decrypt({
                    message: openpgp.message.readArmored(
                        encryption_parameters.encrypted_passphrase
                    ),
                    publicKeys: [public_key],
                    privateKey: private_key,
                    format: 'binary',
                })
                .then(function(decrypted)
                {
                    var deferred = new jQuery.Deferred();
                    self.field_manager.set_encryption_parameters(
                        self, decrypted.data, encryption_parameters.group_id);
                    triplesec.decrypt(
                        {
                            data: new triplesec.Buffer(value, 'base64'),
                            key: new triplesec.Buffer(decrypted.data),
                        },
                        function(error, buffer)
                        {
                            if(error)
                            {
                                // TODO: do something
                                return;
                            }
                            self.set_value(buffer.toString());
                            deferred.resolve(self.get_value());
                        }
                    );
                    return deferred;
                });
            });
        },
    });
}
