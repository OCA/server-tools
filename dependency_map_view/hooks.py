def post_init_hook(env):
    actions = env['ir.actions.act_window'].search([('view_mode', '!=', False)])
    
    for action in actions:
        if 'dependency_map' not in action.view_mode:
            action.view_mode = action.view_mode + ',dependency_map'