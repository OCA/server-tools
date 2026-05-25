The computation of `res.groups.trans_implied_ids` is broken, check it by executing the following steps:
1. Install `sale` module
2. In the Odoo shell execute: `env["res.groups"].get_groups_by_application()`

*Actual result*
`[...,  (ir.module.category(52,), 'boolean', res.groups(22, 21, 20), (100, 'Other')) , ...]`

*Expected result*
`[...,  (ir.module.category(52,), 'selection', res.groups(20, 21, 22), (5, 'Sales')) , ...]`

*Additional info*
The result of `get_groups_by_application` is correct if the computation of `res.groups.trans_implied_ids` is called executing:
`env["res.groups"].search([])._compute_trans_implied()`
