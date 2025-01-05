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
    tracking_uom_id = fields.Many2one(
        related='workorder_id.tracking_uom_id'
    )
    qty_production = fields.Float(
        string="Quantity Produced",
    )

    #===== Compute =====#
    def _compute_duration(self):
        """ Neutralize compute """
        return
    
    @api.depends('duration', 'date_start')
    def _compute_date_end(self):
        for record in self:
            if record.date_start and record.duration:
                record.date_end = fields.Datetime.add(record.date_start, hours=record.duration)

    @api.onchange('workorder_id')
    def _onchange_workorder_id(self):
        if self.workorder_id:
            self.qty_production = 0 if self.workorder_id.productivity_tracking == 'global' else None
