import {onMounted} from "@odoo/owl";
import {ErrorDialog} from "@web/core/errors/error_dialogs";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

patch(ErrorDialog.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.issueAutoSend = session.issue_auto_send || {};
        this.state.issueAutoSendStatus = "idle";
        onMounted(() => {
            if (this.canSendIssueReport() && this.issueAutoSend.auto_send) {
                this.sendIssueReport({automatic: true});
            }
        });
    },

    isIssueReportServerError() {
        return this.props.type === "server" || Boolean(this.props.data?.debug);
    },

    canSendIssueReport() {
        const traceback = this.traceback || this.props.traceback;
        return Boolean(
            (this.issueAutoSend.github || this.issueAutoSend.email) &&
                traceback &&
                this.isIssueReportServerError()
        );
    },

    getIssueReportButtonText() {
        const {github, email} = this.issueAutoSend;
        if (this.state.issueAutoSendStatus === "sending") {
            return _t("Sending...");
        }
        if (this.state.issueAutoSendStatus === "error") {
            return _t("Retry Sending");
        }
        if (this.state.issueAutoSendStatus === "sent") {
            if (github && email) {
                return _t("Report Sent");
            }
            return github ? _t("Sent to GitHub") : _t("Sent by Email");
        }
        if (github && email) {
            return _t("Send Report");
        }
        return github ? _t("Send to GitHub") : _t("Send by Email");
    },

    getIssueReportResultMessage(result) {
        if (result.duplicate) {
            return result.url
                ? _t("This error was already reported: %s", result.url)
                : _t("This error was already reported.");
        }
        const parts = [];
        if (result.github?.ok) {
            parts.push(_t("Sent to GitHub: %s", result.github.url));
        } else if (result.github) {
            parts.push(this.getIssueReportErrorMessage(result.github));
        }
        if (result.email?.ok) {
            parts.push(_t("Sent by email to %s", result.email.email_to.join(", ")));
        } else if (result.email) {
            parts.push(this.getIssueReportErrorMessage(result.email));
        }
        return parts.join("\n");
    },

    getIssueReportErrorMessage(result) {
        const messages = {
            disabled: _t("Automatic error reports are disabled for this company."),
            invalid_url: _t("The GitHub repository URL of this company is invalid."),
            missing_token: _t("No GitHub token is configured for this company."),
            request_failed: _t("GitHub could not be reached."),
            not_configured: _t("Error reports are not configured for this company."),
            missing_email_from: _t(
                "The error report email could not be sent: the company has no email address."
            ),
            email_failed: _t("The error report email could not be sent."),
            github_error: _t(
                "GitHub rejected the report (HTTP %s).",
                result?.status || ""
            ),
        };
        return messages[result?.reason] || _t("Could not send the error report.");
    },

    onClickSendIssueReport() {
        this.sendIssueReport({automatic: false});
    },

    notifyIssueReportResult(result) {
        if (result?.ok) {
            const partialFailure =
                result.github?.ok === false || result.email?.ok === false;
            let type = "success";
            if (result.duplicate) {
                type = "info";
            } else if (partialFailure) {
                type = "warning";
            }
            this.notification.add(this.getIssueReportResultMessage(result), {type});
            return;
        }
        const message =
            result?.github || result?.email
                ? this.getIssueReportResultMessage(result)
                : this.getIssueReportErrorMessage(result);
        this.notification.add(message, {type: "warning"});
    },

    async sendIssueReport({automatic = false} = {}) {
        if (["sending", "sent"].includes(this.state.issueAutoSendStatus)) {
            return;
        }
        this.state.issueAutoSendStatus = "sending";
        let result = null;
        try {
            result = await this.orm.call(
                "res.company",
                "action_send_github_issue",
                [],
                {
                    name: this.title || this.props.name || this.constructor.title || "",
                    message: this.props.message || "",
                    traceback: this.traceback || this.props.traceback || "",
                    context_details: this.contextDetails || "",
                    automatic,
                }
            );
        } catch {
            this.state.issueAutoSendStatus = "error";
            if (!automatic) {
                this.notification.add(_t("Could not send the error report."), {
                    type: "danger",
                });
            }
            return;
        }
        this.state.issueAutoSendStatus = result?.ok ? "sent" : "error";
        if (!automatic) {
            this.notifyIssueReportResult(result);
        }
    },
});
