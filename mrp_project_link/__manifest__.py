# -*- coding: utf-8 -*-
{
    'name': "Project/MRP link",
    'summary': "Organize Work Order by project",
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',
    'license': 'AGPL-3',

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Manufacturing/Manufacturing',
    'version': '16.0.1.0.1',

    'depends': [
        'mrp', # Odoo CE
        'project_favorite_switch', # other
    ],
    'data': [
        # data
        'views/project_project.xml',
        'views/mrp_production.xml',
    ]
}
