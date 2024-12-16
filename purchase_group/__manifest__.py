# -*- coding: utf-8 -*-
{
    'name': 'Reviewers for Account Move validation',
    'summary': "Make sale and purchase user reviewer of account move ",
    'category': 'Accounts',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC, Odoo Community Association (OCA)',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': ['sale', 'purchase', 'account_move_tier_validation'],
    'data': [
        'views/account_move.xml',
    ],
}
