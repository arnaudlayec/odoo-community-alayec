# -*- coding: utf-8 -*-
{
    'name': 'Project Role Visibility',
    'summary': "Use Project's Roles to manage project and tasks visibility for internal users.",
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['project', 'project_role'],
    "data": [
        # views
        "views/project_assignment.xml",
        "views/project_project.xml",
        "views/project_role_views.xml",
        #security
        "security/project_security.xml",
        "security/ir.model.access.csv",
    ],
    "uninstall_hook": "uninstall_hook",
}
