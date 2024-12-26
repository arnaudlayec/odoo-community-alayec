# -*- coding: utf-8 -*-
{
    'name': "Project Budget",
    'summary': "Manage several budgets within a project",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'category': 'Project',
    'version': '16.0.1.0.0',

    'depends': [
        'account_move_budget', # OCA
        'project_budget_line_template',
        'project_favorite_switch'
    ],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/project_budget_security.xml',
        # views
        'views/project_project.xml',
        'views/account_move_budget.xml',
        'views/account_move_budget_line.xml',
        'views/account_analytic_account.xml',
        'views/res_config_settings.xml',
    ],
    "uninstall_hook": "uninstall_hook",
}
