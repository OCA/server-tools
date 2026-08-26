/** @odoo-module **/
/* Copyright 2025 Kencove - Mohamed Alkobrosli
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

export const watchBaseNotificationsService = {
    dependencies: ["bus_service", "notification"],
    async start(env, {bus_service, notification}) {
        bus_service.addEventListener("notification", ({detail: notifications}) => {
            for (const notif of notifications) {
                if (notif.type === "base_notification_updates") {
                    const message =
                        notif.payload && notif.payload.message
                            ? notif.payload.message
                            : notif.payload;
                    notification.add(message, {
                        title: env._t("Notification"),
                        type: "info",
                        sticky: true,
                    });
                }
            }
        });
        await bus_service.addChannel("base_notification_updates");
        await bus_service.start();
    },
};

registry
    .category("services")
    .add("watchBaseNotifications", watchBaseNotificationsService);
