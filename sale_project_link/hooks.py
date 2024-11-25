# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('sale_project_link.seq_sale_order_project_template').unlink()
