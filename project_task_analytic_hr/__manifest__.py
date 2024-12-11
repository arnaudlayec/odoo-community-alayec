# -*- coding: utf-8 -*-
{
    'name': "Project Task HR Analytic",
    'summary': "Use HR analytic in tasks",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Project',
    'version': '16.0.1.0.0',

    'depends': ['project', 'analytic', 'hr_timesheet'],
    'data': [
        'views/account_analytic_account.xml',
        'views/hr_views.xml',
    ]
}


