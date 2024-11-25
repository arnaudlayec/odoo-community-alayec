# -*- coding: utf-8 -*-
{
    'name': "Utilities (file management)",
    'summary': "Technical features for other addons",
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',
    'license': "AGPL-3",

    'application': False,
    'installable': True,
    'category': 'Services',
    'version': '16.0.1.0.0',

    'depends': [
        'base_external_dbsource_mssql',
        'base_external_dbsource_sqlite',
    ],
    'data': ['security/ir.model.access.csv']
}
