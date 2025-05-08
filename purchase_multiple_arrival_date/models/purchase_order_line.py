# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
        store=True,
        readonly=False,
    )

    #===== Compute =====#
    @api.depends('date_arrival_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        """ Fill in `date_planned` when entering a new confirmed Arrival Date
            on the Purchase Order
        """
        res = super()._compute_price_unit_and_date_planned_and_name()
        for line in self:
            line.date_planned = line.date_arrival_id.date_arrival
        return res
    
    @api.depends('date_arrival_id')
    def _compute_date_arrival_confirmed(self):
        print('===_compute_date_arrival_confirmed===')
        for line in self:
            print('line', line)
            print('line.date_arrival_id', line.date_arrival_id)
            line.date_arrival_confirmed = bool(line.date_arrival_id)
