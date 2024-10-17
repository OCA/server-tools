Request is a new type of document that allow user to make approval request with simply approval steps.
Information in the request document is configurable in Request Type window.

**Note:** Although works for a very simple workflow, this module is merely the base. Following are extensions that enhance the feature.

More technical features:

* request_flow_tier_validation: extend base_tier_validation for more flexible approval process
* request_flow_exception: extend base_exception for better exception messages
* request_flow_custom_info: extend base_custom_info for configurable data fields
* request_flow_operating_unit: extend operating_unit for operating units

More child documents, as part of the request process:

* hr_expense_request_flow: for HR Expense
* hr_advance_request_flow: for HR Advance and Clearing
* purchase_request_request_flow: for Purchase Request
