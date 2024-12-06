# -*- coding: utf-8 -*-
{
    'name': 'Project Children Sequence',
    'summary': 'Manage child projects sequence code per parent project (e.g. 1234-01)',
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['project_parent', 'project_sequence'],
    'data': [
        'data/ir_sequence.xml',
        'views/project_project.xml'
    ],
}
