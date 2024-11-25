# -*- coding: utf-8 -*-
{
    'name': 'Task Attachment',
    'summary': 'Adds an attachment field before description, on task form',
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
