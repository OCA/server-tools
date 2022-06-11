odoo.define('example.BasicModel', function (require) {
    "use strict";

    // alert("5454frfr_".includes("_"))

    var BasicModel = require('web.BasicModel');


    BasicModel.include({

        isNew: function (id) {
            var data = this.localData[id];
            if (data.type !== "record") {
                return false;
            }
            var res_id = data.res_id;
            if (typeof res_id === 'number') {
                return false;
            /*
            We need to disable this isInteger check, otherwise the front will not accept
            external ID which are not an integer. 
            We needed to rewrite the function for this, no inheritance possible.
            */
            // } else if (typeof res_id === 'string' && /^[0-9]+-/.test(res_id)) {
            //     return false;
            // }
            } else if (typeof res_id === 'string' && !res_id.includes("_")) {
                return false;
            }
            return true;
        },
    });

});