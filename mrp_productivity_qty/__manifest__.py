# -*- coding: utf-8 -*-
{
    'name': "MRP Productivity Quantity",
    'summary': "Track Work Order productivity by time and produced quantities",
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',
    'license': 'AGPL-3',

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Manufacturing/Manufacturing',
    'version': '16.0.1.0.1',

    'depends': ['mrp'],
    'data': [
        # views
        'views/mrp_workcenter.xml',
        'views/mrp_workorder.xml',
        'views/mrp_productivity.xml',
    ]
}
