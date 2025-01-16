# -*- coding: utf-8 -*-
{
    'name': "MRP Work Center Cost History",
    'summary': "Keep history of workcenter hour costs",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Manufacturing/Manufacturing',
    'version': '16.0.1.0.0',

    'depends': [
        'hr_employee_cost_history',
        'mrp_account',
    ],
    'data': [
        # wizard
        'wizard/cost_history.xml',
        # views
        'views/cost_history.xml',
        'views/mrp_workcenter.xml',
    ],
}
