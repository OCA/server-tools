openerp.disable_openerp_online = function(instance) {
    // Disabling the lookup of a valid OPW for the dbuuid,
    // resulting in 'Your OpenERP is not supported'
    instance.web.WebClient.include({
        show_annoucement_bar: function() {}
    });
};
