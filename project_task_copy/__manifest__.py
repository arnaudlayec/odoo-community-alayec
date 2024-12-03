# -*- coding: utf-8 -*-
{
    'name': 'Task Copy',
    'summary': 'Allow copy Task unitary or in bulk between projects.',
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['project'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # wizard
        'wizard/project_task_copy_wizard.xml',
        # views
        'views/project_task.xml',
    ],
}
