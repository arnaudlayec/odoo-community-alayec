# -*- coding: utf-8 -*-
{
    'name': "Project Task Stage Team Planning",
    'summary': "Allow department managers to review and plan their employee's tasks stages (e.g. daily, weekly, monthly)",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/aluval49/odoo",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'category': 'Project',
    'version': '16.0.1.0.0',

    'depends': ['project'],
    'data': [
        # data
        'data/project.task.type.csv',
        # views
        'views/project_task.xml',
        'views/project_task_type.xml',
    ],
}
