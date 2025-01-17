# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkCenterProductivity(models.Model):
    _inherit = ["mrp.workcenter.productivity"]

    #===== Fields =====#
    duration = fields.Float(
        required=True,
        readonly=False
    )
    date_end = fields.Datetime(
        compute="_compute_date_end",
        store=True
    )
    
    productivity_tracking = fields.Selection(
        related="workorder_id.productivity_tracking"
    )
    product_uom_id = fields.Many2one(
        related='workorder_id.product_uom_id'
    )
    qty_production = fields.Float(
        string="Quantity Produced",
    )
    unit_time = fields.Float(
        compute='_compute_unit_time',
        string='Unit time',
    )

    #===== Onchange =====#
    @api.onchange('workorder_id')
    def _onchange_workorder_id(self):
        if self.workorder_id:
            self.qty_production = False if self.workorder_id.productivity_tracking == 'global' else None

    #===== Compute =====#
    def _compute_duration(self):
        """ Neutralize compute : it becomes writable, and compute `date_end` instead """
        return
    
    @api.depends('duration', 'date_start')
    def _compute_date_end(self):
        for record in self:
            if record.date_start and record.duration:
                record.date_end = fields.Datetime.add(record.date_start, minutes=record.duration)
    
    @api.depends('duration', 'qty_production')
    def _compute_unit_time(self):
        for record in self:
            record.unit_time = record.qty_production and record.duration / record.qty_production