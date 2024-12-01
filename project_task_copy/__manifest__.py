# -*- coding: utf-8 -*-
{
    'name': 'Task Copy',
    'summary': 'Allow to fill main Tasks forms fields from another task.',
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['project'],
    'data': [
        'views/project_task.xml'
    ],
}
