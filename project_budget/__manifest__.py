# -*- coding: utf-8 -*-
{
    'name': "Project Budget",
    'summary': "Manage several budgets within a project",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/aluval49/odoo",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'category': 'Carpentry',
    'version': '16.0.1.0.0',

    'depends': [
        'hr_timesheet', # for allocated_hours
        'account_move_budget', # OCA
        'project_favorite_switch'
    ],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/project_project.xml',
        'views/product_attribute.xml',
        'views/product_product.xml',
        'views/product_template.xml',
        'views/account_move_budget.xml',
        'views/account_move_budget_line.xml',
        'views/account_analytic_account.xml',
    ],
    "uninstall_hook": "uninstall_hook",
}

