# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

from collections import defaultdict

class Task(models.Model):
    _inherit = ['project.task']

    #===== Fields =====#
    available_budget = fields.Float(
        string='Available Budget',
        compute='_compute_available_budget',
        store=True,
        help="[Project budget*] - [Budget* reserved in project's tasks, including this one]"
             " of the task's analytic account"
    )
    
    #===== Compute =====#
    @api.depends(
        # 1. reserved budget in this and other tasks
        'planned_hours', 'project_id.task_ids.planned_hours',
        # 2. task budget category (analytic account)
        'analytic_account_id',
        # 3. available budget in the project
        'project_id', 'project_id.budget_line_ids',
        'project_id.budget_line_ids.qty_balance', 'project_id.budget_line_ids.analytic_account_id'
    )
    def _compute_available_budget(self):
        # Calculate available budget at project level
        project = self.project_id
        mapped_budget = project._get_mapped_budget_line(self.analytic_account_id) # see `project_budget`

        # Map sibling tasks and already reserved budget
        domain = project._get_budget_line_domain(self.analytic_account_id)
        mapped_planned_hours = defaultdict(dict)
        for task in self.search(domain):
            key = (task.project_id.id, task.analytic_account_id.id)
            mapped_planned_hours[key][task.id] = task.planned_hours

        # Re-calculate remaining budget on current task(s), excluding it from its siblings
        for task in self:
            key = (task.project_id.id, task.analytic_account_id.id)
            project_budget = mapped_budget.get(key, 0.0)
            siblings_budget = sum([
                v for k, v in mapped_planned_hours.get(key, {}).items()
                if k != task.id
            ])
            
            task.available_budget = project_budget - siblings_budget - task.planned_hours

            if task.available_budget < 0:
                raise exceptions.UserError(_(
                    'A task cannot reserve more budget than available in the project.'
                    ' Project budget: %s. Already planned budget: %s. This task budget: %s',
                    project_budget, siblings_budget, task.planned_hours
                ))
