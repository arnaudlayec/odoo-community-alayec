# -*- coding: utf-8 -*-
{
    'name': "MRP Attendance",
    'summary': "Operators enters productivity times like in Attendance app",
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',
    'license': 'AGPL-3',

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Manufacturing/Manufacturing',
    'version': '16.0.1.0.1',

    'depends': ['mrp', 'hr_attendance'],
    'data': [
        # security
        'security/mrp_attendance_security.xml',
        'security/ir.model.access.csv',
        # views
        'views/hr_employee.xml',
        'views/mrp_productivity.xml',
        'views/mrp_production.xml',
        'views/mrp_workorder.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_attendance/static/src/**/*',
        ]
    }
}
