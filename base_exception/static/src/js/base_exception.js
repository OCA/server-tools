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

function getActiveRecordInfo(controller) {
    const model = controller.model;
    const root = model?.root;
    return {
        root,
        resModel: root?.resModel,
        resId: root?.resId,
    };
}

async function popUpException() {
    const controller = activeForm.controller;
    const orm = controller.env.services.orm;

    const {resModel, resId} = getActiveRecordInfo(controller);
    if (!resModel || !resId) return false;
    const actionService = controller.env.services.action;
    const action = await orm.call(resModel, "action_popup_exceptions", [[resId]]);
    if (!action) return false;

    await actionService.doAction(action);

    return true;
}

async function refreshExceptionIdsField() {
    const controller = activeForm.controller;
    if (!controller) return false;

    const {root, resModel, resId} = getActiveRecordInfo(controller);
    if (!resModel || !resId) return false;
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
                await popUpException();
            } else {
                throw error;
            }
        }
    },
});
