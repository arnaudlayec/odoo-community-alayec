# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMoveBudgetLine(models.Model):
    _inherit = ["account.move.budget.line"]

    def _update_budget_crud(self, method, fields=[]):
        # Compute `project.allocated_hours`
        if self._should_update(method, fields, ['qty_balance', 'analytic_account_id']):
            self.project_id._update_allocated_hours(method =='unlink' and self.ids)
        
        return super()._update_budget_crud(method, fields)
