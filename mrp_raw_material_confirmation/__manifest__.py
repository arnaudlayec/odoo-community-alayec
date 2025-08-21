# -*- coding: utf-8 -*-
{
    'name': "Raw Material confirmation",
    'summary': "Consume raw materials before fully finishing MOs",
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
    ],
    'data': [
        # data
        'views/mrp_production.xml',
    ]
}
