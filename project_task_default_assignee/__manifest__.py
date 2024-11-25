# -*- coding: utf-8 -*-
{
    'name': 'Project Tasks default assignees',
    'summary': "Auto-assign users to a task depending on the task' type and user's role on project.",
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['project_role', 'project_type'],
    "data": [
        "views/project_type.xml"
    ],
}
