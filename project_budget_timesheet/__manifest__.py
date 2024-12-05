# -*- coding: utf-8 -*-
{
    'name': "Project Budget",
    'summary': "Limit Tasks' planned hours to available budgets",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'auto_install': True,
    'category': 'Project',
    'version': '16.0.1.0.0',

    'depends': ['project_budget', 'hr_timesheet'],
    'data': ['views/project_task.xml'],
}
