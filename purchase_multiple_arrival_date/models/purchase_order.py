# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    date_arrival_ids = fields.One2many(
        comodel_name='purchase.arrival.date',
        inverse_name='order_id',
        string='Confirmed arrivals',
    )
    date_arrival_state = fields.Selection(
        selection=[
            ('none', 'None acknowledged'),
            ('partial', 'Partially acknowledged'),
            ('ok', 'All acknowledged'),
        ],
        string='Arrival confirmation',
        compute='_compute_date_arrival_state',
        store=True,
    )
    date_arrival_attachments = fields.Many2many(
        comodel_name='ir.attachment',
        string='Attachments of Expected arrivals',
        compute='_compute_date_arrival_attachments',
        # inverse='_inverse_date_arrival_attachments',
    )

    #===== Compute =====#
    @api.depends('date_arrival_ids')
    def _compute_date_arrival_attachments(self):
        mapped_data = self._get_order_attachments_mapped()

        for order in self:
            attachment_ids_ = mapped_data.get(order.id, [])
            order.date_arrival_attachments = [Command.set(attachment_ids_)]
    
    # def _inverse_date_arrival_attachments(self):
    #     """ Allow attachment removal, and cascade deletion
    #         to related record of `purchase.arrival.date`
    #     """
    #     Attachment = self.env['ir.attachment']
    #     Arrival = self.env['purchase.arrival.date']
    #     mapped_data = self._get_order_attachments_mapped()

    #     for order in self:
    #         origin = Attachment.browse(mapped_data.get(order.id, []))
    #         removed = origin - order.date_arrival_attachments
    #         if removed:
    #             Arrival.browse(removed.mapped('res_id')).unlink()

    def _get_order_attachments_mapped(self):
        """ Returns a dict like:
            {order_id_: attachment_id_}
        """
        rg_result = self.env['purchase.arrival.date'].read_group(
            domain=[('order_id', 'in', self.ids), ('attachment_id', '!=', False)],
            groupby=['order_id'],
            fields=['attachment_id:array_agg']
        )
        return {x['order_id'][0]: x['attachment_id'] for x in rg_result}
    

    @api.depends('order_line', 'order_line.date_arrival_confirmed')
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
