# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    date_planned_requested = fields.Date(
        # copy of original `date_planned` at creation only (to keep the info)
        string='Requested Arrival',
        compute='_compute_date_planned_requested',
        store=True,
        copy=False,
    )
    date_arrival_ids = fields.One2many(
        comodel_name='purchase.arrival.date',
        inverse_name='order_id',
        domain="[('order_id', '=', id)]",
        string='Confirmed arrivals',
        context={'display_date_ony': 1},
    )
    date_arrival_state = fields.Selection(
        selection=[
            ('none', 'Not acknowledged'),
            ('partial', 'Partially acknowledged'),
            ('ok', 'All acknowledged'),
        ],
        string='Arrival confirmation',
        compute='_compute_date_arrival_state',
        store=True,
        copy=False,
    )
    date_arrival_attachments = fields.Many2many(
        related='date_arrival_ids.attachment_ids',
        string='Attachments of Expected arrivals',
        copy=False,
    )

    #===== Compute =====#
    @api.depends('date_planned')
    def _compute_date_planned_requested(self):
        for order in self:
            if order.state in ['draft', 'cancel'] or not order.date_planned_requested:
                order.date_planned_requested = order.date_planned
    
    @api.depends('order_line', 'order_line.date_arrival_id')
    def _compute_date_arrival_state(self):
        for order in self:
            lines = order.order_line.filtered(lambda x: not x.display_type)
            confirmations = set(lines.mapped('date_arrival_confirmed'))
            
            state = 'partial'
            if confirmations == {False}:
                state = 'none'
            elif confirmations == {True}:
                state = 'ok'
            
            order.date_arrival_state = state
    
    #===== Logics =====#
    def _get_unconfirmed_date_order_line(self):
        return self.order_line.filtered(
            lambda x: not x.date_arrival_id and not x.display_type
        )
    
    #===== Button =====#
    def send_reminder(self):
        template = self.env.ref('purchase.email_template_edi_purchase_reminder', raise_if_not_found=False)
        return self._send_reminder_open_composer(template.id)

    def open_date_arrival_form(self):
        return self._get_date_arrival_action() | {
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    def open_date_arrival_list(self):
        return self._get_date_arrival_action() | {
            'views': [
                (False, 'list'),
                (False, 'calendar'),
                (False, 'pivot'),
                (False, 'form'),
            ],
            'domain': [('order_id', '=', self.id)],
        }
    def _get_date_arrival_action(self):
        xml_id = 'purchase_multiple_arrival_date.action_open_arrival_date'
        return self.env['ir.actions.act_window']._for_xml_id(xml_id)
    