openerp.oerp_develop_test_mode = function(instance) {
    _t = instance.web._t;

    instance.web.WebClient.include({
        show_application: function() {
            return $.when(this._super.apply(this, arguments)).then(this.proxy('show_mode_bar'));
        },
        show_mode_bar: function() {
            var $bar = this.$el.find('.mode_bar');
            $bar.css('display', 'none');
            var $mode_message = this.$el.find('.mode_message');
            this.rpc("/web/mode/get_mode", {'db': this.session.db, 'mode': 'test'}).always(function (ret_val){
                if (ret_val){
                    $bar.css('display', '');
                    $bar.css('color', 'white');
                    $bar.css('background','red');
                    $mode_message.text('Test Environment')
                }
            })
            this.rpc("/web/mode/get_mode", {'db': this.session.db, 'mode': 'develop'}).always(function (ret_val){
                if (ret_val){
                    $bar.css('display', '');
                    $bar.css('color', 'white');
                    $bar.css('background','navy');
                    $mode_message.text('Development Environment')
                }
            })
        }
    });
}
