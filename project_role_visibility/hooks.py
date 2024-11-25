# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api

def uninstall_hook(cr, registry):
    """ Restore initial menus """
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('project_role.project_menu_config_roles').write({
        'parent_id': env.ref('project.menu_project_config')
    })
    env.ref('project_role.menu_project_assignments').write({
        'parent_id': env.ref('project.menu_main_pm')
    })
