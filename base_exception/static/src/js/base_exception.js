import {patch} from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";
import {FormController} from "@web/views/form/form_controller";

// keep track of the current FormController by storing it
const activeForm = {
    controller: null,
};

patch(FormController.prototype, {
    setup() {
        super.setup();
        activeForm.controller = this;
    },
    willUnmount() {
        if (activeForm.controller === this) {
            activeForm.controller = null;
        }
        super.willUnmount();
    },
});

async function refreshExceptionIdsField() {
    const controller = activeForm.controller;
    if (!controller) return false;

    const model = controller.model;
    const root = model?.root;
    const resModel = root?.resModel;
    const resId = root?.resId;

    if (!resModel || !resId) return false;

    // Use services from the controller's env (OWL environment)
    const orm = controller.env.services.orm;

    // Read the latest value for just that field
    await orm.read(resModel, [resId], ["exception_ids"]);

    // Reload the record; OWL will re-render the field
    await root.load();
    return true;
}

patch(rpc, {
    async _rpc(url, params = {}, settings = {}) {
        try {
            return await super._rpc(url, params, settings);
        } catch (error) {
            if (
                error.exceptionName ===
                "odoo.addons.base_exception.exceptions.BaseExceptionError"
            ) {
                await refreshExceptionIdsField();
                // Swallow the error so no stacktrace dialog appears.
                // Return a never-resolving promise to stop further handling cleanly
                return new Promise(() => {});
            }
            throw error;
        }
    },
});
