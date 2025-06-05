# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line']

    date_arrival_id = fields.Many2one(
        comodel_name='purchase.arrival.date',
        string='Confirmed Arrival date',
        ondelete='set null',
        copy=False,
    )
    date_arrival_confirmed = fields.Boolean(
        string='Confirmed Arrival',
        compute='_compute_date_arrival_confirmed',
    )
    price_unit_verified = fields.Boolean(
        string='Verified price',
        related='date_arrival_id.price_unit_verified',
    )
    
    #===== Compute =====#
    def _compute_date_planned_arrival(self):
        """ Compute `date_planned` as per arrival_date
            Should not be executed on order.line with empty `date_arrival_id`
            so that draft po have an initial `planned_date`
        """
        for line in self:
            line.date_planned = line.date_arrival_id.date_arrival
    
    @api.depends('date_arrival_id')
    def _compute_date_arrival_confirmed(self):
        for line in self:
            line.date_arrival_confirmed = bool(line.date_arrival_id)
