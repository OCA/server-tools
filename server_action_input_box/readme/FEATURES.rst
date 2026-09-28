- **Perfect Integration:** The application seamlessly integrates with Odoo Server Actions. You can access it by clicking on "Actions with Parameters" through the "Technical" menu in the Actions section.

- **User-Friendly Interface:** Users can configure the target model where the action will be performed, the parameters to be requested from the input box, and the Python code of the action using the environment variables specific to Server Actions and the variables associated with user-created parameters in this application.

- **Flexible Configuration:** The module allows users to specify as many parameters as needed. They can choose a "one2many" field of the target model as the set of records on which the action will be performed. Users can select whether the action will be performed in bulk (the same parameter value for all) or individually (configure the parameter value one by one for each record).

- **Security:** While all code configuration is done through this module, its execution takes place within a Server Action, ensuring the inherent security and reliability of the Odoo environment. Optionally, it includes a confirmation box to appear at the moment of executing the action, providing the opportunity to cancel at the last moment.
