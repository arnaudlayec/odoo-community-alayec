# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command, _

class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'project.default.mixin']

    #===== Fields =====#
    project_id = fields.Many2one(
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    
    #===== CRUD: sequence =====#
    @api.model_create_multi
    def create(self, vals_list):
        vals_list = self._sale_project_modify_vals_list(vals_list)
        return super().create(vals_list)

    def _sale_project_modify_vals_list(self, vals_list):
        # Perf optim: get all project ids at once
        project_ids_ = [vals.get('project_id') for vals in vals_list if vals.get('project_id')]
        mapped_project_ids = {x.id: x for x in self.env['project.project'].browse(project_ids_)}

        for vals in vals_list:
            project_id = mapped_project_ids.get(vals.get('project_id'))
            if project_id:
                vals |= (
                    self._get_seq_name(project_id, vals)
                    | self._get_vals_from_project(project_id, should_erase=False, vals=vals)
                )
        return vals_list
    
    @api.model
    def _get_seq_name(self, project_id, vals):
        """ Generate Sale Order's sequence like `1234-001` where 1234
            is project's code and 001 sequence of the project for its Sale Orders
        """
        name_key = {}
        if 'company_id' in vals:
            project_id = project_id.with_company(vals['company_id'])
        if vals.get('name', _("New")) == _("New"):
            # create the per-project sequence for Sale Order, if not existing already
            if not project_id.sale_order_sequence_id.id:
                project_id._create_sale_order_sequence_one()
            name_key = {'name': project_id.sale_order_sequence_id.next_by_id()}
        
        return name_key

    def _get_vals_from_project(self, project_id=None, should_erase=True, vals=None):
        """ :option project_id: for `create()`
            :option should_erase: if we should keep Sale Order's vals or erase them with Project's vals
            :option vals: must be given if `should_erase=False`
        """
        project_id = project_id or self.project_id
        return {
            field: (project_id[field].id if hasattr(project_id[field], '_name') else project_id[field])
            for field in self._get_fields_from_project()
            if should_erase or not vals.get(field)
        }
    def _get_fields_from_project(self):
        """ Can be overwritten """
        return ['partner_id', 'analytic_account_id']
    

    #===== Onchange (vals & line analytic) =====#
    @api.onchange('project_id')
    def _onchange_project_id(self):
        """ Auto-populates SO fields from project's ones, and lines analytic """
        project_analytics = self.env.company.analytic_plan_id.account_ids

        for sale_order in self:
            # SO fields
            vals = sale_order._get_vals_from_project()
            if vals:
                sale_order.write(vals)
            
            # SO lines analytics
            sale_order.order_line._replace_analytic(
                replaced_ids=project_analytics._origin.ids,
                added_id=sale_order.project_id.analytic_account_id._origin.id
            )


    #===== Invoice =====#
    def _prepare_invoice(self):
        return super()._prepare_invoice() | {
            'project_id': self.project_id.id
        }
    