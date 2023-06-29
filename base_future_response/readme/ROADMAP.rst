This module monkey patches the request object as soon as it is imported. The patch is
not reverted when the module is uninstalled. It should be totally harmless though, since
it simply adds a ``future_response`` attribute to the request object, and does not
change the response if cookies or headers are added to future_response.
