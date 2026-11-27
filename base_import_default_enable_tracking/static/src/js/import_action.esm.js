/* Copyright 2024 Simone Rubino - Aion Tech
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {ImportAction} from "@base_import/import_action/import_action";
import {patch} from "@web/core/utils/patch";

patch(ImportAction.prototype, {
    setup() {
        super.setup(...arguments);
        // Enable history tracking by default
        this.model.importOptionsValues.tracking_disable.value = false;
    },
});
