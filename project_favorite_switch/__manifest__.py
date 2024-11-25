# -*- coding: utf-8 -*-
{
    'name': 'Project Favorite Switch',
    'summary': 'Allow to select its favorite projects from right corner of top menu bar of any screens.',
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
        # views
        'views/project_views_favorite.xml',
        # wizard
        'wizard/project_choice_wizard.xml'
    ],
    'assets': {
        'web.assets_backend': ['project_favorite_switch/static/src/**/*']
    },
}
