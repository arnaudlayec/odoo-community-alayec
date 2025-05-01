# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

from collections import defaultdict

class Task(models.Model):
    _inherit = ['project.task']

    #===== Fields method =====#
    @api.model
    def _read_group_analytic(self, analytics, domain, order):
        """ Show all timesheetable in column, in task's kanban view """

        domain = ['|', ('id', 'in', analytics.ids), ('timesheetable', '=', True)]
        analytics = (
            analytics.sudo()
            .with_context(display_short_name=True, display_analytic_budget=True)
            .search(domain, order=order)
        )
        
        # If project can be guessed, limit columns to the ones with budget line(s) on the project
        project_id_ = self.env['project.default.mixin']._get_project_id()
        domain = [('budget_line_ids.project_id', '=', project_id_)]

        return analytics if not project_id_ else analytics.filtered_domain(domain)
    
    @api.model
    def default_get(self, fields):
        """ By default, Task analytic follow kanban column (context) """
        vals = super().default_get(fields)

        column_analytic = self._context.get('default_analytic_account_id')
        if column_analytic:
            vals['analytic_account_id'] = column_analytic

        return vals


    #===== Fields =====#
    analytic_account_id = fields.Many2one(
        domain="""[
            ('timesheetable', '=', True),
            ('budget_line_ids.project_id', '=', project_id),
            '|', ('company_id', '=', False), ('company_id', '=', company_id),
        ]""",
        group_expand='_read_group_analytic' # for kanban columns
    )
    available_budget = fields.Float(
        string='Available Budget',
        compute='_compute_available_budget',
        help="[Project budget] - [Planned hours of project's tasks, including this one]. "
             "Can be negative, in contrary of real budget reservation in below table."
    )
    
    @api.depends(
        # 1. reserved budget in this and other tasks
        'planned_hours', 'analytic_account_id', # 2.
        'project_id.task_ids.planned_hours',
        # 3. available budget in the project
        'project_id', 'project_id.budget_line_ids',
        'project_id.budget_line_ids.qty_balance',
    )
    def _compute_available_budget(self):
        # Calculate available budget at project level
        project = self.project_id.with_context(analytic_ids=self.analytic_account_id.ids)
        mapped_budget = project._get_mapped_budget_line(
            field='qty_balance',
            groupby=['project_id', 'analytic_account_id']
        )

        # Map sibling tasks and already reserved budget
        domain = project._get_budget_line_domain()
        mapped_planned_hours = defaultdict(dict)
        for task in self.search(domain):
            key = (task.project_id.id, task.analytic_account_id.id)
            mapped_planned_hours[key][task.id] = task.planned_hours

        # Re-calculate remaining budget on current task(s), excluding it from its siblings
        for task in self:
            key = (task.project_id.id, task.analytic_account_id.id)
            project_budget = mapped_budget.get(key, 0.0)
            siblings_planned_hours = sum([
                v for k, v in mapped_planned_hours.get(key, {}).items()
                if k != task.id
            ])
            
            task.available_budget = project_budget - siblings_planned_hours - (task.planned_hours or 0.0)

            # if task.available_budget < 0:
            #     raise exceptions.UserError(_(
            #         'A task cannot reserve more budget than available in the project.\n'
            #         'Project budget: %s.\n Already planned budget: %s.\n This task budget: %s',
            #         project_budget, siblings_budget, task.planned_hours
            #     ))
