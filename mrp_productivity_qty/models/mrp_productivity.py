# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkCenterProductivity(models.Model):
    _inherit = ["mrp.workcenter.productivity"]

    #===== Fields =====#
    # tracking & qty
    productivity_tracking = fields.Selection(related="workorder_id.productivity_tracking")
    product_uom_id = fields.Many2one(related='workorder_id.product_uom_id')
    qty_production = fields.Float(string="Quantity Produced")
    unit_time = fields.Float(string='Unit time', compute='_compute_performance')
    # performance of the entry
    performance = fields.Float(string='Performance (%)', compute='_compute_performance')
    gain = fields.Float(string='Gain', compute='_compute_performance')
    # performance of the workorder
    wo_qty_production = fields.Float(related='workorder_id.qty_production')
    wo_duration_hours_expected = fields.Float(string='Expected Duration', compute='_compute_performance')
    wo_duration_hours = fields.Float(string='Total Duration done', compute='_compute_performance')
    wo_qty_produced = fields.Float(string='Total Produced Quantity', compute='_compute_performance')
    wo_qty_remaining = fields.Float(string='Remaining to produce', compute='_compute_performance')
    wo_unit_time_avg = fields.Float(related='workorder_id.unit_time_avg')
    wo_unit_time_real = fields.Float(
        string='Realized unit time', compute='_compute_performance',
        help='Total on the workorder, including current time'
    )
    wo_performance = fields.Float(string='Total Performance (%)', compute='_compute_performance')
    wo_gain = fields.Float(string='Total Gain', compute='_compute_performance')
    wo_progress_qty = fields.Float(string='Total Progress Done (%)', compute='_compute_performance', digits=(16, 0))
    wo_progress = fields.Float(string='Total Progress Time (%)', compute='_compute_performance', digits=(16, 0))

    #===== Onchange =====#
    @api.onchange('workorder_id')
    def _onchange_workorder_id(self):
        self.qty_production = False

    #===== Compute =====#
    @api.depends('duration', 'qty_production', 'workorder_id', 'workorder_id')
    def _compute_performance(self):
        _compute_metrics = self.env['mrp.workorder']._compute_metrics
        for record in self:
            # productivity
            record.unit_time, record.performance, record.gain = _compute_metrics(
                record.wo_unit_time_avg, record.duration, record.qty_production
            )

            # workorder quantities & duration
            wo = record.workorder_id
            record.wo_duration_hours_expected = wo.duration_expected / 60
            wo_duration = wo.duration - record._origin.duration + record.duration
            record.wo_duration_hours = wo_duration / 60
            record.wo_qty_produced = wo.qty_produced - record._origin.qty_production + record.qty_production
            record.wo_qty_remaining = wo.qty_remaining + record._origin.qty_production - record.qty_production

            # workorder performance
            record.wo_unit_time_real, record.wo_performance, record.wo_gain = _compute_metrics(
                record.wo_unit_time_avg, wo_duration, record.wo_qty_produced
            )
            record.wo_progress_qty = record.wo_qty_remaining and record.wo_qty_produced / record.wo_qty_remaining * 100 # as per qties
            record.wo_progress = wo.duration_expected and wo_duration / wo.duration_expected * 100 # as per times
