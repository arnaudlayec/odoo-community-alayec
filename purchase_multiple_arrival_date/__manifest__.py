# -*- coding: utf-8 -*-
{
    'name': 'Purchase Multiple Arrival Dates',
    'summary': "Helps managing multiple arrival dates confirmed from suppliers",
    'category': 'Inventory/Purchase',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['purchase'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/purchase_order_line.xml',
        'views/purchase_arrival_date.xml',
        'views/purchase_order.xml',
        'views/res_partner.xml',
    ],
}
