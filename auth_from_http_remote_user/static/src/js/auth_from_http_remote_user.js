openerp.auth_from_http_remote_user = function(instance) {

    instance.web.Session.include({
        session_load_response : function(response) {
            //unregister the event since it must be called only if the rpc call
            //is made by session_reload
            this.off('response', this.session_load_response);
            if (response.error && response.error.data.type === "session_invalid") {
                $("body").html("<h1>Access Denied</h1>");
            }
            
            console.log("session_load_response called");
        },
        
        session_reload : function() {
            var self = this;
            // we need to register an handler for 'response' since
            // by default, the rpc doesn't call callback function
            // if the response is of error type 'session_invalid'
            this.on('response', this, this.session_load_response); 
            return this.rpc("/web/session/get_http_remote_user_session_info", {
                db : $.deparam.querystring().db
            }).done(function(result) {
                // If immediately follows a login (triggered by trying to
                // restore
                // an invalid session or no session at all), refresh session
                // data
                // (should not change, but just in case...)
                _.extend(self, result);
            }).fail(function(result){
                $("body").html("<h1>Server error</h1>");
            });
        }
    });

};