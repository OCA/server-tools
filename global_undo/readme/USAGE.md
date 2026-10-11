Press **Ctrl+Z** to undo the last thing you did, **Ctrl+Shift+Z** to redo it.
The shortcuts are deliberately registered without `bypassEditableProtection`:
inside an `input` or a `textarea`, Ctrl+Z keeps its native meaning of "undo
what I just typed" and never reaches the server.

The systray also carries an undo icon, a redo icon and a history dropdown with
the ten most recent steps. Each button names in its tooltip the step it would
act on and is disabled when there is none, so the shortcut never quietly undoes
something other than what it announces.

The undo stack behaves like the one in any editor. Ctrl+Z takes the most
recently applied step, Ctrl+Shift+Z takes the oldest undone one, so repeated
redos walk back up the stack in the order it was unwound. Any new operation
discards the redo stack.

## Trash

Deleted records are listed under *Settings > Global Undo > Trash* and can be
restored from there. To bring back a parent and its children, select them all
and restore them in one go: the trash applies the same ordering and the same id
remapping as an undo, so the children come back pointing at the parent's new
id. Restoring only a child leaves it orphaned.

## History

*Settings > Global Undo > Undo History* lists every recorded step, its
operations, and lets a step be undone or redone from the form view. Ordinary
users see only their own; a Global Undo Administrator sees everyone's.
