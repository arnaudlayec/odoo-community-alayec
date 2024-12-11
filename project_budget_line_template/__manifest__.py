# -*- coding: utf-8 -*-
{
    'name': "Project Budget Line Template",
    'summary': "Ease filling-in budget line with suggestions",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Project',
    'version': '16.0.1.0.0',

    'depends': ['account_move_budget'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/account_move_budget_line_template.xml',
    ],
}
