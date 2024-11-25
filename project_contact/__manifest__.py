# -*- coding: utf-8 -*-
{
    'name': 'Project Contact',
    'summary': 'Allow to manage a contacts list per project, independently of project sharing features',
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['project'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/project_contact.xml',
        'views/project_project.xml',
        'views/res_partner.xml'
    ],
}
