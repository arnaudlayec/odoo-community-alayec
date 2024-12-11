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
    
    # @api.depends(
    #     'budget_line_ids',
    #     'budget_line_ids.qty_balance',
    #     'budget_line_ids.analytic_account_id',
    #     'budget_line_ids.analytic_account_id.timesheetable',
    # )
    def _update_allocated_hours(self, remove_budget_ids):
        # Get sum of `qty_balance` for timesheetable budgets
        # see module `project_budget`
        self = self.with_context(timesheetable=True, remove_budget_ids=remove_budget_ids)
        mapped_budget = self._get_mapped_budget_line(field='qty_balance')
        for project in self:
            project.allocated_hours = mapped_budget.get(project.id)


    def _get_budget_line_domain(self):
        """ Overwrite from module `project_budget` """
        domain = super()._get_budget_line_domain()

        analytic_ids = self._context.get('analytic_ids')
        if analytic_ids:
            domain += [('analytic_account_id', 'in', analytic_ids)]
        
        if self._context.get('timesheetable'):
            domain += [('analytic_account_id.timesheetable', '=', True)]
        
        remove_budget_ids = self._context.get('remove_budget_ids')
        if self._context.get('remove_budget_ids'):
            domain += [('id', 'not in', remove_budget_ids)]

        return domain
