# -*- coding: utf-8 -*-
{
    'name': "Project Budget Workforce",
    'summary': "Value budget lines through date-ranged HR costs",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Project',
    'version': '16.0.2.0.0',

    'depends': [
        'hr_employee_cost_history',
        'hr_department_cost_history', # for search
        'project_budget_timesheet'
    ],
    'data': [
        'views/account_move_budget_line.xml',
        'views/hr_employee_timesheet_cost_history.xml',
        'views/account_analytic_account.xml',
        # security
        'security/ir.model.access.csv',
    ],
}
