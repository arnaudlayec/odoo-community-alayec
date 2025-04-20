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
        'mrp',
    ],
    'data': [
        # views
        'views/stock_picking.xml',
        'views/mrp_production.xml',
        # report
        'report/stock_report_picking_operations.xml',
        'report/mrp_production_template.xml',
    ],
}
