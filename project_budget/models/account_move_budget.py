# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMoveBudget(models.Model):
    _name = "account.move.budget"
    _inherit = ["account.move.budget", "project.default.mixin"]

    #===== Fields =====#
    project_id = fields.Many2one(
        required=False, # keep possibility of budgets independant of any project
        ondelete='set null'
    )
    template = fields.Boolean(
        string='Template',
        default=False,
        help='If activated, this budget will be selectable to be copied from, on other projects.'
    )
    template_default_project = fields.Boolean(
        string='Template (default)',
        default=False,
        help='If activated, this budget will be suggested by default for all new projects.'
    )

    #===== Onchange =====#
    @api.onchange('project_id')
    def _onchange_project_id(self):
        self._synchro_fields_with_project()

    #===== Logics =====#
    def _synchro_fields_with_project(self):
        """ Called from `write()` of project.project """
        for budget in self:
            # synchronize `name`
            budget.name = budget.project_id.display_name

            # always synch. date start & end, but /!\ they are optional in the project
            if budget.project_id.date_start:
                budget.date_from = budget.project_id.date_start
            if budget.project_id.date:
                budget.date_to = budget.project_id.date
