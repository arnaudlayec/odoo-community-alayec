# -*- coding: utf-8 -*-
{
    'name': 'Stock Packaging Enforce',
    'summary': "Ensure the respect of packaging in Purchase Orders",
    'category': 'Inventory/Inventory',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'product',
    ],
    'data': [
        # views
        'views/sale_order.xml'
    ],
}
