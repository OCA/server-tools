/** @odoo-module **/

import {attr} from "@mail/model/model_field";
import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "Attachment",
    modelMethods: {
        convertData(data) {
            const data2 = this._super(data);
            if ("create_date" in data) {
                data2.create_date = data.create_date;
            }
            if ("create_user" in data) {
                data2.create_user = data.create_user;
            }
            return data2;
        },
    },
    fields: {
        create_date: attr(),
        create_user: attr(),
    },
});
