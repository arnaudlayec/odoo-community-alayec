# -*- coding: utf-8 -*-
{
    'name': 'Project Image',
    'summary': 'Adds an image field to project form',
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['project'],
    'data': [
        'views/project_views_image.xml'
    ],
}
