This module allows displaying logs when server actions are executed:

1.  a log is generated as soon as an action starts
2.  a log is generated if the action is completed without any exception
    being raised, and the log displays the duration (in seconds) of the
    action itself
3.  if action's field `Enable SQL Debug` is set, queries are logged too
    during the action's execution
