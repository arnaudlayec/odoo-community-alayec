# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line']

    date_arrival_id = fields.Many2one(
        comodel_name='purchase.arrival.date',
        string='Confirmed Arrival date',
        ondelete='set null',
    )
    date_arrival_confirmed = fields.Boolean(
        string='Confirmed Arrival',
        compute='_compute_date_arrival_confirmed',
    )
    price_unit_verified = fields.Boolean(
        string='Verified price',
        related='date_arrival_id.price_unit_verified',
    )

    @api.constrains('date_arrival_id')
    def _constrain_date_arrival_id(self):
        for line in self:
            line.date_arrival_id._constrain_order_consistency()
    
    @api.depends('date_arrival_id')
    def _compute_date_arrival_confirmed(self):
        for line in self:
            line.date_arrival_confirmed = bool(line.date_arrival_id)
