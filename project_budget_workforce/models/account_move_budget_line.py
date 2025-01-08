# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMoveBudgetLine(models.Model):
    _inherit = ["account.move.budget.line"]

    #===== Fields =====#
    type = fields.Selection(
        selection_add=[('workforce', 'Workforce')],
        ondelete={'workforce': 'set unit'},
        help='- "Amount": Debit and Credit are filled in\n'
             '- "Unit": Qty Debit, Qty Credit and Unit Price are filled in, and'
             ' Debit and Credit are calculated accordingly\n'
             '- "Workforce": same as "Unit" but Unit Price is calculated as per HR\n'
             ' history costs of the budget line\'s Analytic Account.'
    )
    timesheet_cost_history_ids = fields.One2many(
        related="analytic_account_id.timesheet_cost_history_ids",
    )


    #===== Compute: valuation =====#
    @api.depends(
        'qty_debit', 'qty_credit', 'standard_price',
        'budget_id', 'budget_id.date_from', 'budget_id.date_to',
        'analytic_account_id',
        'timesheet_cost_history_ids',
        'timesheet_cost_history_ids.hourly_cost',
        'timesheet_cost_history_ids.starting_date'
    )
    def _compute_debit_credit(self):
        """ Overwrite only for @api.depends() """
        return super()._compute_debit_credit()
    
    def _compute_debit_credit_one(self):
        """ Overwrite to add dated-valuation logic as per `timesheet_cost_history_ids` """
        self.ensure_one()
        if self.type != 'workforce':
            return super()._compute_debit_credit_one()
        
        _value_workforce = self.sudo().analytic_account_id._value_workforce
        self.debit = _value_workforce(self.qty_debit, self.budget_id)
        self.credit = _value_workforce(self.qty_credit, self.budget_id)
    