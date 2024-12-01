# -*- coding: utf-8 -*-
{
    'name': 'Sale-Project link',
    'summary': "Create and organize your sales by projects",
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': [
        'sale', 'sale_project', # Odoo 
        'project_sequence', # OCA
        'project_favorite_switch'
    ],
    'data': [
        # data
        'data/ir.sequence.xml',
        # views
        'views/project_project.xml',
        'views/sale_order.xml'
    ],
    'uninstall_hook': 'uninstall_hook',
}
