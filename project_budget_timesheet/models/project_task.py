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
    remaining_budget = fields.Float(
        string='Remaining Budget',
        compute='_compute_remaining_budget',
        help="[Project budget] - [Planned hours of project's tasks, including this one]"
    )
    
    @api.depends(
        # 1. reserved budget in this and other tasks
        'planned_hours', 'analytic_account_id', # 2.
        'project_id.task_ids.planned_hours',
        # 3. available budget in the project
        'project_id', 'project_id.budget_line_ids',
        'project_id.budget_line_ids.qty_balance',
    )
    def _compute_remaining_budget(self):
        # 1. Calculate available budget at project level
        domain = self.project_id._get_domain_update_allocated_hours(
            analytic_account_ids=self.analytic_account_id.ids
        )
        rg_result = self.env['account.move.budget.line'].sudo()._read_group(
            domain=[('project_id', '!=', False)] + domain,
            fields=['qty_balance:sum'],
            groupby=['project_id', 'analytic_account_id'],
            lazy=False,
        )
        mapped_budget = {
            (x['project_id'][0], x['analytic_account_id'][0]): x['qty_balance']
            for x in rg_result
        }

        # 2. Map sibling tasks and already reserved budget
        mapped_planned_hours = defaultdict(dict)
        for task in self.search(domain):
            key = (task.project_id.id, task.analytic_account_id.id)
            mapped_planned_hours[key][task.id] = task.planned_hours

        # 3. Calculate remaining budget on current task(s), excluding it from its siblings
        for task in self:
            key = (task.project_id.id, task.analytic_account_id.id)
            project_budget = mapped_budget.get(key, 0.0)
            siblings_planned_hours = sum([
                v for k, v in mapped_planned_hours.get(key, {}).items()
                if k != task.id
            ])
            
            task.remaining_budget = project_budget - siblings_planned_hours - (task.planned_hours or 0.0)
