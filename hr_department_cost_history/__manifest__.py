# -*- coding: utf-8 -*-
{
    'name': "HR Department Cost History",
    'summary': "Manage Hourly Cost per department and keep history",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Services/Timesheets',
    'version': '16.0.1.0.0',

    'depends': ['hr_employee_cost_history'],
    'data': [
        # wizard
        'wizard/hr_employee_timesheet_cost_wizard.xml',
        # views
        'views/hr_employee_timesheet_cost_history.xml',
        'views/hr_department.xml',
    ],
}
