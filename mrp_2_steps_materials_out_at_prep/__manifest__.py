{
    'name': "MRP 2 steps: materials out at preparation",
    'summary': "MO's components stock decreases at PREP validation instead of MO validation.",
    'author': 'Arnaud LAYEC',
    'website': 'https://github.com/arnaudlayec/odoo-community-carpentry',
    'license': 'AGPL-3',

    'application': False,
    'installable': True,
    'auto_install': False,
    'category': 'Manufacturing/Manufacturing',
    'version': '16.0.1.0.1',

    'depends': ['mrp'],
    "data": [
        "views/mrp_production.xml",
        "wizard/mrp_immediate_production.xml",
    ]
}
