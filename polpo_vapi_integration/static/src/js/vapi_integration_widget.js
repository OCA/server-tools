$(document).ready(function () {

    function toOdooDatetime(dateObj) {
        const pad = n => n < 10 ? '0' + n : n;
        return dateObj.getFullYear() + '-' +
            pad(dateObj.getMonth() + 1) + '-' +
            pad(dateObj.getDate()) + ' ' +
            pad(dateObj.getHours()) + ':' +
            pad(dateObj.getMinutes()) + ':' +
            pad(dateObj.getSeconds());
    }


    function showVapiWidget() {

        $.ajax({
            url: '/polpo_vapi_integration/widget_config',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({}),
            success: function (res) {
                var config = res.result;


                // Wait for vapiSDK to be available
                var tryRun = function () {
                    if (!window.vapiSDK || !window.vapiSDK.run) {
                        setTimeout(tryRun, 200);
                        return;
                    }

                    const instance = window.vapiSDK.run({

                        apiKey: config.api_key,
                        assistant: config.assistant_id,
                        assistantOverrides: {
                            firstMessage: "Hola " + config.userName + ", ¿cómo estás?",
                            variableValues: {
                                userData: config.userData,
                                companyData: config.companyData,
                                fechaHora: new Date().toLocaleDateString()
                            },
                            metadata: {
                            }
                        },
                        message: {
                        },
                        config: {
                        }
                    });

                    let logId = null;
                    let statusUpdated = false;

                    instance.on('call-start', () => {
                        callStartTime = new Date();

                        const callId = 'call_' + Date.now();
                        fetch('/web/dataset/call_kw/vapi.log/create', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            credentials: 'include',
                            body: JSON.stringify({
                                jsonrpc: "2.0",
                                method: "call",
                                params: {
                                    model: "vapi.log",
                                    method: "create",
                                    args: [{
                                        user_id: config.userId,
                                        start_time: toOdooDatetime(callStartTime),
                                        state: "started",
                                        call_id: callId
                                    }],
                                    kwargs: {}
                                },
                                id: Math.floor(Math.random() * 1000000)
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            logId = data.result;

                        })
                        .catch(error => console.error("Error:", error));
                    });

                    instance.on('message', function(message) {

                        if (
                            message.type === 'transcript' &&
                            message.role === 'user' &&
                            message.transcriptType === 'final'
                        ) {
                            if (logId && !statusUpdated) {
                                statusUpdated = true;
                                fetch('/web/dataset/call_kw/vapi.log/write', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-Requested-With': 'XMLHttpRequest'
                                    },
                                    credentials: 'include',
                                    body: JSON.stringify({
                                        jsonrpc: "2.0",
                                        method: "call",
                                        params: {
                                            model: "vapi.log",
                                            method: "write",
                                            args: [
                                                [logId],
                                                {
                                                    state: "in_progress",
                                                    last_active: toOdooDatetime(new Date())
                                                }
                                            ],
                                            kwargs: {}
                                        },
                                        id: Math.floor(Math.random() * 1000000)
                                    })
                                })
                                .then(response => response.json())
                                .then(data => {

                                })
                                .catch(error => console.error("Error:", error));
                            } else if (logId) {

                                fetch('/web/dataset/call_kw/vapi.log/write', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-Requested-With': 'XMLHttpRequest'
                                    },
                                    credentials: 'include',
                                    body: JSON.stringify({
                                        jsonrpc: "2.0",
                                        method: "call",
                                        params: {
                                            model: "vapi.log",
                                            method: "write",
                                            args: [
                                                [logId],
                                                {
                                                    last_active: toOdooDatetime(new Date())
                                                }
                                            ],
                                            kwargs: {}
                                        },
                                        id: Math.floor(Math.random() * 1000000)
                                    })
                                })
                                .then(response => response.json())
                                .then(data => {

                                })
                                .catch(error => console.error("Error:", error));
                            }
                        }
                    });

                    instance.on('call-end', () => {
                        callEndTime = new Date();

                        if (callStartTime) {
                            const duration = Math.floor((callEndTime - callStartTime) / 1000);

                            fetch('/web/dataset/call_kw/vapi.log/write', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-Requested-With': 'XMLHttpRequest'
                                },
                                credentials: 'include',
                                body: JSON.stringify({
                                    jsonrpc: "2.0",
                                    method: "call",
                                    params: {
                                        model: "vapi.log",
                                        method: "write",
                                        args: [
                                            [logId],
                                            {
                                                end_time: toOdooDatetime(callEndTime),
                                                duration: duration,
                                                state: "finished"
                                            }
                                        ],
                                        kwargs: {}
                                    },
                                    id: Math.floor(Math.random() * 1000000)
                                })
                            })
                            .then(response => response.json())
                            .then(data => {

                            })
                            .catch(error => console.error("Error:", error));

                        }
                    });

                };
                tryRun();
            }
        });
    }

    // For testing purposes, run it automatically when the page loads:
    showVapiWidget();

    // Or you can call it from wherever you want in your flow.
});
