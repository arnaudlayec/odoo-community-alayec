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
        required=True,
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
    duration = fields.Float(readonly=True)
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
    progress_qty = fields.Float(
        string="Progress (qty)",
        compute="_compute_qty_produced",
        store=True
    )
    unit_time_avg = fields.Float(string='Planned unit time', compute='_compute_performance') # in hours !
    unit_time_real = fields.Float(string='Realized unit time', compute='unit_time_real') # in hours !
    performance = fields.Float(string='Performance (%)', compute='_compute_performance')
    gain = fields.Float(string='Gain', compute='_compute_performance')

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

            wo.unit_time_avg = wo.duration_expected and wo.duration_expected / wo.qty_production / 60
            wo.unit_time_real, wo.performance, wo.gain = wo._compute_metrics(
                wo.unit_time_avg, duration, qty_produced
            )

    @api.model
    def _compute_metrics(self, unit_time_avg, duration, qty_produced):
        """ :arg unit_time_avg: h/unit
            :arg duration:      in min
            :arg qty_procuded:  /
            :return: unit_time_real (h/unit), performance, gain (h)
        """
        unit_time_real = qty_produced and duration / qty_produced / 60 or 0
        performance = 0
        gain = 0

        if unit_time_avg and unit_time_real:
            performance = -1 * (unit_time_real - unit_time_avg) / unit_time_avg * 100
            gain = -1 * (unit_time_real - unit_time_avg) * qty_produced

        return unit_time_real, performance, gain

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
            wo.progress_qty = wo.qty_production and wo.qty_produced / wo.qty_production * 100

    def button_finish(self):
        """ Neutralize change on `qty_produced` """
        mapped_qty_produced = {x.id: x.qty_produced for x in self}
        res = super().button_finish()
        for wo in self:
            wo = mapped_qty_produced.get(wo.id)
        return res
