# -*- coding: utf-8 -*-
{
    'name': 'Reviewers for Account Move validation',
    'summary': "Validate purchase invoice by buyer",
    'category': 'Accounts',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC, Odoo Community Association (OCA)',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': ['purchase', 'account_move_tier_validation'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/security.xml',
        # views
        'views/account_move.xml',
    ],
}
