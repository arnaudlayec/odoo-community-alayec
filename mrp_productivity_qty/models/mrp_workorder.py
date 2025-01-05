# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkOrder(models.Model):
    _inherit = ["mrp.workorder"]

    # user-defined
    productivity_tracking = fields.Selection([
        ('global', "Global"),
        ('unit', "Quantitative")
    ], string="Productivity Tracking")
    tracking_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure'
    )
    qty_production = fields.Float(
        string="Quantity to Produce",
        required=True,
        readonly=False,
        related='' # unset `related`, so it becomes user-defined per Work Order
    )

    # computed
    time_ids = fields.One2many(
        comodel_name='mrp.workcenter.productivity',
        inverse_name='workorder_id',
        string="Productivity Times"
    )
    qty_produced = fields.Float(
        string="Quantity Produced",
        compute="_compute_qty_produced",
        store=True
    )
    performance = fields.Integer(
        compute='_compute_performance'
    )

    #===== Onchange (default) =====#
    @api.onchange('workcenter_id')
    def _onchange_workcenter_id(self):
        for wo in self:
            if wo.workcenter_id:
                wo.productivity_tracking = wo.workcenter_id.productivity_tracking
                wo.tracking_uom_id = wo.workcenter_id.tracking_uom_id

    #===== performance & qty_produced (compute & button) =====#
    @api.depends('qty_production', 'qty_produced', 'duration_expected', 'duration')
    def _compute_performance(self):
        for wo in self:
            unit_time_avg = wo.duration_expected and wo.qty_production / wo.duration_expected
            unit_time_real = wo.qty_produced and wo.duration / wo.qty_produced

            if unit_time_avg and unit_time_real:
                wo.performance = -1 * (unit_time_real - unit_time_avg) / unit_time_avg * 100

    @api.depends('time_ids', 'time_ids.qty_production')
    def _compute_qty_produced(self):
        rg_result = self.env['mrp.workcenter.productivity'].read_group(
            domain=[('workorder_id', 'in', self.ids)],
            groupby=['workorder_id'],
            fields=['qty_production:sum'],
        )
        mapped_data = {x['workorder_id'][0]: x['qty_production'] for x in rg_result}

        for wo in self:
            wo.qty_produced = mapped_data.get(wo.id, 0.0)

    def button_finish(self):
        """ Neutralize change on `qty_produced` """
        mapped_qty_produced = {x.id: x.qty_produced for x in self}
        res = super().button_finish()
        for wo in self:
            wo = mapped_qty_produced.get(wo.id)
        return res
