# -*- coding: utf-8 -*-
{
    'name': 'CRM-Project link',
    'summary': "Convert Opportunities to Projects and link them",
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC, Odoo Community Association (OCA)',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['project', 'crm'],
    'data': [
        'views/project_project.xml',
        'views/crm_lead.xml'
    ],
}
