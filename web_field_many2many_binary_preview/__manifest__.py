# -*- coding: utf-8 -*-
{
    'name': 'Open Multiple Attachments Fields',
    'summary': "Opens multiple attachments fields instead of downloading them",
    'category': 'Hidden',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['web', 'mail'],
    'assets': {
        'web.assets_backend': [
            'web_field_many2many_binary_preview/static/src/**/*',
        ]
    }
}
