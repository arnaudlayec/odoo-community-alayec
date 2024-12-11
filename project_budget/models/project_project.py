# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from collections import defaultdict

from datetime import timedelta

class Project(models.Model):
    _inherit = ["project.project"]
    
    #===== Fields' methods =====#
    def _default_budget_template_ids(self):
        domain = [('template_default_project', '=', True)]
        default_budget_ids = self.env['account.move.budget'].sudo().search(domain)
        return [Command.set(default_budget_ids.ids)]
    
    #===== Fields =====#
    budget_ids = fields.One2many(
        comodel_name='account.move.budget',
        inverse_name='project_id',
        string="Budget sheets",
        copy=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True
    )
    budget_template_ids = fields.One2many(
        # UI-field only, to copy budget template into `budget_ids`
        comodel_name='account.move.budget',
        string='Budget templates',
        domain=[('template', '=', True)],
        default=_default_budget_template_ids,
        compute='_compute_budget_template_ids',
        inverse='_inverse_budget_template_ids',
    )
    budget_line_ids = fields.One2many(
        comodel_name='account.move.budget.line',
        inverse_name='project_id',
        string='Budget lines'
    )
    budget_line_sum = fields.Monetary(
        string='Budget Sum',
        currency_field='currency_id',
        compute='_compute_budget_line_sum',
        store=True
    )
    date_start = fields.Date(
        help='Required for budget (start and end).'
    )


    #===== CRUD =====#
    def write(self, vals):
        """ Synchro `name`, `date_from`, `date_to` with budget """
        res = super().write(vals)
        if any(x in vals for x in ['name', 'date_start', 'date']):
            self.sudo().budget_ids._synchro_fields_with_project()
        return res
    
    
    #===== Compute (sums) =====#
    @api.depends('budget_line_ids', 'budget_line_ids.balance')
    def _compute_budget_line_sum(self):
        """ Sum the balance of budget lines to show it in project's form smart button """
        mapped_data = self._get_mapped_budget_line()
        for project in self:
            project.budget_line_sum = mapped_data.get(project.id)
    
    def _get_mapped_budget_line(self, field='balance', groupby=['project_id']):
        """ `field` is used in other module `project_budget_timesheet` """
        lazy = bool(len(groupby) == 1)
        rg_result = self.env['account.move.budget.line'].sudo().read_group(
            domain=self._get_budget_line_domain(),
            fields=[field + ':sum'],
            groupby=groupby,
            lazy=lazy
        )
        return {
            x[groupby[0]][0] if lazy else tuple([x[key] and x[key][0] for key in groupby]): x[field]
            for x in rg_result
        }
    
    def _get_budget_line_domain(self):
        """ Overwritten in module `project_budget_timesheet` """
        return [('project_id', 'in', self.ids)]
    
    
    #===== Compute (budget templates) =====#
    def _compute_budget_template_ids(self):
        default_budget_ids_cmd = self._default_budget_template_ids()
        for project in self:
            project.budget_template_ids = default_budget_ids_cmd
    
    def _inverse_budget_template_ids(self):
        """    a) Copy selected budgets templates
            or b) create 1 default empty budget per project
        """
        empty_project_ids = self._filter_without_budgets()
        for project in empty_project_ids:
            for budget_tmpl in project.budget_template_ids:
                budget_new = budget_tmpl.sudo().copy(project._get_default_vals_budget())

                # *manually* copy the lines (because of date constrain)
                for line in budget_tmpl.line_ids:
                    vals = project._get_default_vals_budget_line(budget_new)
                    line.sudo().copy(vals)
                
                empty_project_ids -= project
        
        # Create an empty budget
        vals_list_budget = [project._get_default_vals_budget() for project in empty_project_ids]
        self.env['account.move.budget'].sudo().create(vals_list_budget)

    def _filter_without_budgets(self):
        return self.filtered(lambda x: not x.budget_ids.ids)

    def _get_default_vals_budget(self, vals={}):
        return {
            'project_id': self.id,
            'name': self.display_name,
            'date_from': self.date_start or fields.Date.today(),
            'date_to': self.date or fields.Date.today() + timedelta(days=1),
            'company_id': self.company_id.id,
            'line_ids': [Command.clear()], # don't copy `line_ids` yet (because of `date` constrain)
            'template': False,
            'template_default_project': False
        } | vals
    
    def _get_default_vals_budget_line(self, budget_id, vals={}, default=False):
        default = 'default_' if default else ''

        return {
            default + 'project_id': self.id,
            default + 'partner_id': self.partner_id.id,
            default + 'budget_id': budget_id.id,
            default + 'date': self._get_default_project_budget_line_date(budget_id)
        } | vals
    
    def _get_default_project_budget_line_date(self, budget_id):
        """ Tries `today` if within budget dates, else `budget_id.date_from` """
        today = fields.Date.today()
        return (
            today if (budget_id.date_from and today > budget_id.date_from) and (budget_id.date_to and today < budget_id.date_to)
            else budget_id.date_from
        )

    #===== Button =====#
    def button_open_budget_lines(self):
        self.ensure_one()
        budget_id = fields.first(self.budget_ids)
        view_id_ = self.env.ref('project_budget.view_account_move_budget_line_tree_simplified').id
        context = self._get_default_vals_budget_line(budget_id, vals={'default_type': 'amount'}, default=True)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.budget.line',
            'view_mode': 'tree',
            'view_id': view_id_, # simplified budget lines view for projects 
            'name': _('Budget lines'),
            'context': context,
            'domain': [('project_id', '=', self.id)]
        }
