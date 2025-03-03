# -*- coding: utf-8 -*-
{
    'name': "HR Holidays On-Behalf for Managers",
    'summary': "Managers create their employees' leaves on their behalf",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Human Resources',
    'version': '16.0.1.0.0',

    'depends': ['hr_holidays'],
    'data': [
        # security
        'security/hr_holidays_security.xml',
        # views
        'views/hr_leave.xml',
        'views/hr_leave_allocation.xml',
    ],
}
