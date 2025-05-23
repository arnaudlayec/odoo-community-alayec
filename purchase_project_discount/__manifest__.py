# -*- coding: utf-8 -*-
{
    'name': 'Purchase Project Discount',
    'summary': "Automate discount of Purchase Orders per projects and vendors",
    'category': 'Inventory/Purchase',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['purchase', 'purchase_order_general_discount', 'project_favorite_switch'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/project_project.xml',
        'views/purchase_project_discount.xml',
    ],
}
