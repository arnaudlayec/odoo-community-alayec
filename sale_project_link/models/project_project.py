# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectProject(models.Model):
    _inherit = "project.project"

    #===== Fields =====#
    sale_order_sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Sale Order sequence',
        check_company=True,
        copy=False
    )
    sale_order_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='project_id',
        string='Sale Orders'
    )
    sale_order_count = fields.Integer(
        string='Quotations & Sale Orders count',
        compute='_compute_sale_order_fields',
        compute_sudo=True
    )
    sale_order_sum = fields.Monetary(
        string='Quotations & Sale Orders total amount',
        compute='_compute_sale_order_fields',
        store=True
    )
    

    #===== CRUD: sequence of Sale Orders =====#
    def _create_sale_order_sequence_one(self):
        """ Creates 1 sequence per project, for sale orders """
        self.ensure_one()

        seq_tmpl = self.env.ref('sale_project_link.seq_sale_order_project_template')
        seq_new = seq_tmpl.sudo().with_company(self.company_id.id).copy()
        seq_new.write({
            'code': seq_tmpl.code + '_' + self.sequence_code,
            'name': _('Sale Order sequence of project ') + self.display_name,
            'prefix': self.sequence_code + seq_tmpl.prefix,
            'company_id': self.company_id.id,
        })

        self.sale_order_sequence_id = seq_new

    def unlink(self):
        if self.sale_order_sequence_id.id:
            self.sale_order_sequence_id.unlink()
        return super().unlink()


    #===== Compute =====#
    @api.depends('sale_order_ids', 'sale_order_ids.amount_untaxed')
    def _compute_sale_order_fields(self):
        fields = self._get_rg_sale_order_fields()

        rg_result = self.env['sale.order'].sudo().read_group(
            domain=[('project_id', 'in', self.ids), ('state', '!=', 'cancel')],
            fields=[field[1] for field in fields],
            groupby=['project_id'],
        )
        # reformat rg_result, being able to extend requested fields in `read_group`
        mapped_data = {
            x['project_id'][0]: {
                field[0]: x.get(field[2]) for field in fields
            } for x in rg_result
        }
        for project in self:
            for field in fields:
                project[field[0]] = mapped_data.get(project.id, {}).get(field[0])
    def _get_rg_sale_order_fields(self):
        """ Can be overritten:
            0. field of `project.project`
            1. field of `read_group()`
            2. field of `rg_result`
        """
        return {
            ('sale_order_count', 'project_id', 'project_id_count'),
            ('sale_order_sum', 'amount_untaxed:sum', 'amount_untaxed')
        }
