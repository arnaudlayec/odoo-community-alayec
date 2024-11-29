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
    allocated_hours = fields.Float(
        # overwrite origin field
        compute='_compute_allocated_hours',
        readonly=True
    )
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
        compute='_compute_budget_line_sum',
        currency_field='currency_id',
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
            self.budget_ids._synchro_fields_with_project()
        return res
    
    
    #===== Compute (sums) =====#
    @api.depends('budget_line_ids', 'budget_line_ids.balance')
    def _compute_budget_line_sum(self):
        """ Sum the balance of budget lines to show it in project's form smart button """
        rg_result = self.env['account.move.budget.line'].sudo().read_group(
            domain=[('project_id', 'in', self.ids)],
            fields=['balance:sum'],
            groupby=['project_id'],
        )
        mapped_data = {x['project_id'][0]: x['balance'] for x in rg_result}
        for project in self:
            project.budget_line_sum = mapped_data.get(project.id)
    
    
    @api.depends(
        'budget_ids.line_ids',
        'budget_ids.line_ids.qty_balance',
        'budget_ids.line_ids.product_tmpl_id',
        'budget_ids.line_ids.product_tmpl_id.uom_id',
        'budget_ids.line_ids.product_tmpl_id.uom_id.category_id',
    )
    def _compute_allocated_hours(self):
        """ Find and groupsum hours in budget """
        # Get sum of `qty_balance` for budgets of working-time category
        uom_whour = self.env.ref('uom.product_uom_hour')
        domain = [
            ('project_id', 'in', self.ids),
            ('qty_balance', '!=', 0),
            ('product_tmpl_id.uom_id.category_id', '=', uom_whour.category_id.id)
        ]
        rg_result = self.env['account.move.budget.line'].sudo().read_group(
            domain=domain,
            groupby=['project_id', 'product_tmpl_id'],
            fields=['qty_balance:sum'],
            lazy=False
        )

        # `product_tmpl_id` to `uom_id`: for conversion of `product_tmpl_id.uom_id` to hours
        product_tmpl_ids_ = [x['product_tmpl_id'][0] for x in rg_result]
        pivot_product_to_uom = {
            x.id: x.uom_id
            for x in self.env['product.template'].sudo().search([('id', 'in', product_tmpl_ids_)])
        }

        # Convert `qty_balance` in hour (if needed)
        mapped_data = defaultdict(int)
        for x in rg_result:
            line_uom_id = pivot_product_to_uom.get(x['product_tmpl_id'][0])
            qty_in_hour = line_uom_id._compute_quantity(x['qty_balance'], uom_whour)
            mapped_data[x['project_id'][0]] += qty_in_hour

        for project in self:
            project.allocated_hours = mapped_data.get(project.id)


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
            for budget in project.budget_template_ids:
                budget_id = budget.copy(project._get_default_vals_budget())
                # *manually* copy the lines because of date constrain
                budget_id.line_ids = [
                    Command.link(line.copy(self._get_default_vals_budget_line(budget)).id)
                    for line in budget.line_ids
                ]
                empty_project_ids -= project
        
        # Create an e
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
            'line_ids': [Command.clear()], # don't copy `line_ids` because of `date` constrain
            'template': False,
            'template_default_project': False
        } | vals
    def _get_default_vals_budget_line(self, budget, vals={}):
        return {
            'budget_id': budget.id,
            'date': budget.date_from
        } | vals

    #===== Button =====#
    def button_open_budget_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.budget.line',
            'view_mode': 'tree,form',
            'name': _('Budget lines'),
            'context': {
                'default_project_id': self.id
            },
            'domain': [('project_id', '=', self.id)]
        }
