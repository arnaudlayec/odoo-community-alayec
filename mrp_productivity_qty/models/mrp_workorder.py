# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkOrder(models.Model):
    _inherit = ["mrp.workorder"]

    #===== Fields =====#
    # user-defined
    productivity_tracking = fields.Selection([
            ('global', "Global"),
            ('unit', "Quantitative")
        ], string="Productivity Tracking",
        default=lambda self: self.workcenter_id.productivity_tracking
    )
    product_uom_id = fields.Many2one(
        # native re-used field
        readonly=False,
        required=False,
        default=lambda self: self.workcenter_id.product_uom_id.id
    )
    qty_production = fields.Float(
        string="Quantity to Produce",
        required=True,
        readonly=False,
        related='' # unset `related`, so it becomes user-defined per Work Order
    )

    # computed
    duration = fields.Float(
        readonly=True
    )
    progress_duration = fields.Float(
        compute='_compute_performance',
        string='Progress (as per spent time)'
    )
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
    unit_time_avg = fields.Float(
        compute='_compute_performance',
        string='Unit time (planned)',
    )
    unit_time_real = fields.Float(
        compute='unit_time_real',
        string='Unit time (real)',
    )
    performance = fields.Float(
        compute='_compute_performance',
        string='Performance (%)',
    )
    gain = fields.Float(
        compute='_compute_performance',
        string='Gain',
    )

    #===== Onchange (default) =====#
    @api.onchange('workcenter_id')
    def _onchange_workcenter_id(self):
        for wo in self:
            if wo.workcenter_id:
                wo.productivity_tracking = wo.workcenter_id.productivity_tracking
                wo.product_uom_id = wo.workcenter_id.product_uom_id

    #===== performance & qty_produced (compute & button) =====#
    @api.depends(
        'qty_production', 'duration_expected',
        'time_ids', 'time_ids.duration', 'time_ids.qty_production'
    )
    def _compute_performance(self):
        for wo in self:
            # use `sum` so it's real-time
            duration = sum(wo.time_ids.mapped('duration'))
            qty_produced = sum(wo.time_ids.mapped('qty_production'))

            wo.unit_time_avg = wo.duration_expected and wo.duration_expected / wo.qty_production
            wo.unit_time_real = qty_produced and duration / qty_produced

            perf, gain = 0, 0
            if wo.unit_time_avg and wo.unit_time_real:
                perf = -1 * (wo.unit_time_real - wo.unit_time_avg) / wo.unit_time_avg * 100
                gain = -1 * (wo.unit_time_real - wo.unit_time_avg) * qty_produced
            
            wo.gain = gain
            wo.performance = perf
            wo.progress_duration = wo.duration_expected  and duration / wo.duration_expected * 100

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
