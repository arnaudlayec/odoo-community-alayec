# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _

class AccountAnalyticAccount(models.Model):
    """ Configuration on Analytic Account for Project Budget """
    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account', 'account.move.budget.update.mixin']
    # native: 
    # _order = 'plan_id, name'
    _order = 'plan_id, sequence, code, name'

    sequence = fields.Integer(
        # used in account.move.budget.line:
        # budget lines sequence follows analytic account's sequence
    )
    is_project_budget = fields.Boolean(
        string='Is project budget?',
        compute='_compute_is_project_budget',
        search='_search_is_project_budget',
    )
    budget_type = fields.Selection(
        selection=[
            ('goods', 'Goods'),
            ('service', 'Service')
        ],
        string='Budget type',
    )
    budget_only_accountant = fields.Boolean(
        string='Accountant budget only?',
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
    @api.depends('budget_type')
    def _compute_is_project_budget(self):
        for analytic in self:
            analytic.is_project_budget = bool(analytic.budget_type)
    
    def _search_is_project_budget(self, operator, value):
        if value not in (True, False) or operator not in ('=', '!='):
            raise exceptions.UserError(_("Operation not supported."))
        is_budget = bool(operator == '=' and value) or bool(operator == '!=' and not value)
        operator = '!=' if is_budget else '='
        return [('budget_type', operator, False)]
    
    @api.model
    def _search_budget_project_ids(self, operator, value):
        """ Analytic used in budget lines of some projects (value) """
        domain = [('project_id', operator, value)]
        lines = self.env['account.move.budget.line'].search(domain)
        return [('id', 'in', lines.analytic_account_id.ids)]
