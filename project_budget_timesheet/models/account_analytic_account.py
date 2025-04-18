# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang


class AccountAnalyticAccount(models.Model):
    _inherit = ['account.analytic.account']

    #===== Fields methods =====#
    def _get_timesheetable_types(self):
        return ['service']

    def name_get(self):
        """ Overwrites native, for Tasks Kanban view groupped by Analytic Account
            - don't display `code` in `display_name` prefix (but display it elsewhere)
            - if single project is display, show amount of budget loaded to this analytic
               in the displayed project
        """
        # Get budgets per projects
        mapped_budgets = {}
        if self._context.get('display_analytic_budget') == True:
            project_id_ = self.env['project.default.mixin']._get_project_id()
            if project_id_:
                rg_result = self.env['account.move.budget.line'].sudo().read_group(
                    domain=[('project_id', '=', project_id_), ('analytic_account_id', 'in', self.ids)],
                    groupby=['analytic_account_id'],
                    fields=['qty_balance:sum']
                )
                mapped_budgets = {x['analytic_account_id'][0]: x['qty_balance'] for x in rg_result}
        
        res = []
        for analytic in self:
            name = analytic.name

            # Conditionnally show `code` prefix, cf. `project_task.py`
            if not self._context.get('display_short_name') and analytic.code:
                name = '[{}] {}' . format(analytic.code, name)

            # keep native (partner after name)
            if analytic.partner_id.commercial_partner_id.name:
                name = f'{name} - {analytic.partner_id.commercial_partner_id.name}'

            # Append budget in the project (if possible)
            budget_amount = mapped_budgets.get(analytic.id, 0.0)
            if budget_amount or self._context.get('display_analytic_budget'):
                budget_amount = formatLang(self.env, budget_amount, dp='Product Unit of Measure')
                name += ' ({}h)' . format(budget_amount)
            
            # add clock for timesheetable

            res.append((analytic.id, name))
        return res


    #===== Fields =====#
    timesheetable = fields.Boolean(
        compute='_compute_timesheetable',
        store=True
    )
    budget_line_ids = fields.One2many(
        # for analytic account domain in `project.task`
        comodel_name='account.move.budget.line',
        inverse_name='analytic_account_id',
        string='Budget lines'
    )

    #===== CRUD =====#
    def _update_budget_crud(self, method, fields=[]):
        # Compute `project.allocated_hours`
        if self._should_update(method, fields, ['timesheetable']):
            remove_budget_ids = bool(method == 'unlink') and self.budget_line_ids.ids
            self.budget_line_ids.project_id._update_allocated_hours(remove_budget_ids)
        
        return super()._update_budget_crud(method, fields)

    @api.depends('budget_type')
    def _compute_timesheetable(self):
        types = self._get_timesheetable_types()
        for analytic in self:
            analytic.timesheetable = analytic.budget_type in types
