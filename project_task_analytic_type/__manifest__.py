# -*- coding: utf-8 -*-
{
    'name': "Project Task Type Analytic",
    'summary': "Set Task analytic based on Type",
    'author': "Arnaud LAYEC",
    'website': "https://github.com/arnaudlayec/odoo-community-alayec",
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Project',
    'version': '16.0.1.0.0',

    'depends': ['project_type', 'analytic'],
    'data': ['views/project_type.xml']
}
