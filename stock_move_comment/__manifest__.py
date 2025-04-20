# -*- coding: utf-8 -*-
{
    'name': 'Stock Move Comment',
    'summary': "Adds `Comment` field in Stock Move and reports (picking & manufacturing orders' components)",
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
