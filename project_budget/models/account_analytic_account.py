# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    """ Configuration on Analytic Account for Project Budget """
    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account', 'account.move.budget.update.mixin']

    sequence = fields.Integer(
        # used in account.move.budget.line: budget lines sequence follows analytic account's sequence
    )
    budget_only_accountant = fields.Boolean(
        string='Accountant only?',
        default=True,
        help='If checked, projects managers will not be able to select it in budgets.'
    )
    budget_type = fields.Selection(
        selection=[
            ('goods', 'Goods'),
            ('service', 'Service')
        ],
        string='Budget type',
    )


    def _get_default_line_type(self):
        """ Defines default `type` of account.move.budget.line """
        return 'unit' if self.budget_type == 'service' else 'amount'
