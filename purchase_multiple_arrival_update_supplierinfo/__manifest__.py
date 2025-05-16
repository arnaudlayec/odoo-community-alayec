# -*- coding: utf-8 -*-
{
    'name': 'Purchase Multiple Arrival: Update Supplier Info',
    'summary': "Helps accountants to control and update supplier prices from POs acknowledgment.",
    'category': 'Inventory/Purchase',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['product', 'purchase_multiple_arrival_date'],
    'data': [
        # views
        'views/purchase_order.xml',
        'views/purchase_order_line.xml',
    ],
}
