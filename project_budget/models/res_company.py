# -*- coding: utf-8 -*-

from odoo import fields, models, _

class ResCompany(models.Model):
    _inherit = ["res.company"]

    analytic_budget_plan_id = fields.Many2one(
        comodel_name='account.analytic.plan',
        string="Analytic Plan for Project Budgets",
        check_company=True,
        readonly=False,
        compute="_compute_analytic_budget_plan_id",
        help="This plan gathers analytic accounts on which budget can be defined"
             " per projects and expensed on Purchase Orders, Timesheets, etc."
             " via analytic distribution or tasks."
    )

    def _compute_analytic_budget_plan_id(self):
        """ Create a default separate plan for budget analytic """
        for company in self:
            # Fetch modified config or already created plan, if any
            budget_plan = (
                self.env['ir.config_parameter'].with_company(company).sudo()
                .get_param("project_budget_analytic_plan_id_%s" % company.id)
            )
            company.analytic_budget_plan_id = int(budget_plan) if budget_plan else False

            # If not configured yet, create specific default plan for budgets
            if not company.analytic_budget_plan_id:
                company.analytic_budget_plan_id = (
                    self.env['account.analytic.plan'].with_company(company).create({
                        'name': _('Project Budgets'),
                        'company_id': self.env.company.id,
                    })
                )

    def write(self, vals):
        for company in self:
            if 'analytic_budget_plan_id' in vals:
                self.env['ir.config_parameter'].sudo().set_param(
                    "project_budget_analytic_plan_id_%s" % company.id,
                    vals['analytic_budget_plan_id']
                )
        return super().write(vals)
