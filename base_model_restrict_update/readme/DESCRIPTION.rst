This module add global model access restriction on top of user current access right.

There are 2 method to choose from,

1. Model Restriction: restrict update on some model, allow some users to edit.

    This method adds a config to apply a global update restriction to specific model,
    while only certain users can update the records if the config is enabled.

2. User Restriction: readonly access on all model for some users.

    This method first setup all user to have access to all model as normal,
    then adminstrator can restrict only some user to be a readonly user.
