# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    """ Configuration on Analytic Account for Project Budget """
    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account', 'account.move.budget.update.mixin']

    sequence = fields.Integer(
        # used in account.move.budget.line: budget lines sequence follows analytic account's sequence
    )
    is_project_budget = fields.Boolean(
        compute='_compute_is_project_budget',
        search='_search_is_project_budget'
    )
    budget_type = fields.Selection(
        selection=[
            ('goods', 'Goods'),
            ('service', 'Service')
        ],
        string='Budget type',
    )
    budget_only_accountant = fields.Boolean(
        string='Accountant only?',
        default=True,
        help='If checked, projects managers will not be able to select it in budgets.'
    )
    budget_project_ids = fields.Many2many(
        comodel_name='project.project',
        search='_search_budget_project_ids',
        store=False
    )

    def _get_default_line_type(self):
        """ Defines default `type` of account.move.budget.line """
        return 'unit' if self.budget_type == 'service' else 'amount'

    #===== Compute =====#
    def _compute_is_project_budget(self):
        """ Configuration per company defining if the analytic account
            can be used as a project's budget in budget lines
        """
        budget_plan = self.company_id.analytic_budget_plan_id
        for analytic in self:
            analytic.is_project_budget = bool(analytic.plan_id == budget_plan)

    @api.model
    def _search_is_project_budget(self, operator, value):
        budget_plan = self.env.company.analytic_budget_plan_id
        return [('plan_id', '=', budget_plan.id)]
    
    @api.model
    def _search_budget_project_ids(self, operator, value):
        """ Analytic used in budget lines of some projects (value) """
        domain = [('project_id', operator, value)]
        lines = self.env['account.move.budget.line'].search(domain)
        return [('id', 'in', lines.analytic_account_id.ids)]
