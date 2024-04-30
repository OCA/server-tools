This module adds a way to log server actions:

* before an action starts running, a log at INFO level is produced saying: ``Running action with id %s and name %s``
* after the action has run, a log in INFO level is produced saying ``Action with id %s and name %s took %s seconds``, and giving the duration of the execution
