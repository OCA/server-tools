import {registry} from "@web/core/registry";

/* eslint-disable no-unused-vars */
async function popUpException(env, _action) {
    /* eslint-enable no-unused-vars */
    const controller = env.services.action.currentController;
    const orm = env.services.orm;
    const resId = controller.currentState?.resId;
    const resModel = controller.props.resModel;
    if (!resModel || !resId) return;
    const popupAction = await orm.call(resModel, "action_popup_exceptions", [[resId]]);
    if (!popupAction) return;
    // Do a soft reload before displaying the popup to display the exception
    // on the Form view
    await env.services.action.restore(controller.jsId);
    await env.services.action.doAction(popupAction);
}

function baseExceptionErrorHandler(env, uncaughtError, originalError) {
    const controller = env.services.action.currentController;
    if (
        originalError.exceptionName ===
        "odoo.addons.base_exception.exceptions.BaseExceptionError"
    ) {
        const excData = JSON.parse(originalError.data.message);
        if (excData.target_model === controller.props.resModel) {
            env.services.action.doAction({
                type: "ir.actions.client",
                tag: "popup_exception",
            });
        } else {
            env.services.action.doAction({
                type: "ir.actions.client",
                tag: "soft_reload",
            });
        }
        return true;
    }
}

registry.category("actions").add("popup_exception", popUpException);
registry
    .category("error_handlers")
    .add("base_exception_error", baseExceptionErrorHandler, {sequence: 0});
