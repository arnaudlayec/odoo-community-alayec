# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    _inherit = ['account.analytic.account']

    sequence = fields.Integer(
        # so all project's budget lines follows the same sequence
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Default Product',
        domain=[('budget_ok', '=', True)],
        help='For budget, this product will be pre-selected in budget lines linked to'
             ' this analytic account, which itself allows:\n'
             ' 1. pre-selection of Account from product\'s expense account (or product\'s'
             ' category\'s in budget lines;\n'
             ' 2. date-ranged valuation of budget lines, as per product variant cost per'
             ' date range.'
    )
