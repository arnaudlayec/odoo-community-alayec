# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command

class Project(models.Model):
    _inherit = ["project.project"]
    
    # allocated_hours = fields.Float(
        # /!\ ORM ignores any computation, maybe because it is already a store field in `hr_timesheet`
        # compute='_compute_allocated_hours',
        # readonly=True,
        # store=True
    # )
    
    @api.depends('budget_line_ids.qty_balance')
    def _compute_budget_line_sum(self):
        return super()._compute_budget_line_sum()
    
    # @api.depends(
    #     'budget_line_ids',
    #     'budget_line_ids.qty_balance',
    #     'budget_line_ids.analytic_account_id',
    #     'budget_line_ids.analytic_account_id.timesheetable',
    # )
    def _update_allocated_hours(self, removed_budget_ids):
        # Get sum of `qty_balance` for timesheetable budgets
        rg_result = self.env['account.move.budget.line'].sudo()._read_group(
            domain=self._get_domain_update_allocated_hours(removed_budget_ids),
            fields=['qty_balance:sum'],
            groupby=['project_id'],
        )
        mapped_data = {x['project_id'][0]: x['qty_balance'] for x in rg_result}

        for project in self:
            project.allocated_hours = mapped_data.get(project.id, 0.0)

    def _get_domain_update_allocated_hours(self, removed_budget_ids=None, analytic_account_ids=None):
        """ Overwrite from module `project_budget` """
        domain = [
            ('project_id', 'in', self._origin.ids),
            ('analytic_account_id.timesheetable', '=', True),
        ]
        
        if removed_budget_ids:
            domain += [('id', 'not in', removed_budget_ids)]

        if analytic_account_ids:
            domain += [('analytic_account_id', 'in', analytic_account_ids)]

        return domain
