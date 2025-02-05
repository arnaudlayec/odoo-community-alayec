# -*- coding: utf-8 -*-
{
    'name': 'Purchase Readonly User',
    'summary': "Readonly user for purchase",
    'category': 'Project',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-alayec',

    'application': False,
    'installable': True,
    'depends': ['purchase'],
    'data': ['security/purchase_security.xml', 'security/ir.model.access.csv'],
}
