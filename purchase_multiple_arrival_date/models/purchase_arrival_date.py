# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command, exceptions, _

class PurchaseArrivalDate(models.Model):
    _name = 'purchase.arrival.date'
    _description = 'Purchase Arrival Date'
    _rec_names_search = ['date_arrival', 'order_id', 'partner_id']

    #===== Fields methods =====#
    def default_get(self, fields):
        """ Pre-fill `order_line` with remaining not-confirmed-yet lines """
        vals = super().default_get(fields)
        order = self.env['purchase.order'].browse(
            vals.get('order_id') or self._context.get('default_order_id')
        )
        if order and 'order_line' in fields:
            vals['order_line'] = [Command.set(order._get_unconfirmed_date_order_line().ids)]
        return vals
    
    @api.depends('date_arrival', 'order_id')
    def _compute_display_name(self):
        for arrival in self:
            arrival.display_name = (
                arrival.date_arrival
                if self._context.get('display_date_ony') else
                arrival.order_id.name
            )

    #===== Fields =====#
    order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        required=True,
        ondelete='cascade',
        help='Products on which the Arrival Date will apply. '
             'Pre-filled with yet unconfirmed products.'
    )
    partner_id = fields.Many2one(
        related='order_id.partner_id',
    )
    date_arrival = fields.Date(
        # required=True in the view but not in the model
        # so record of `purchase.arrival.date` can be created
        # without a date from `purchase_order()`.`_inverse_date_arrival_attachments()`
        string='Arrival Date',
        default=lambda self: fields.Date.today(),
    )
    attachment = fields.Binary(string='File')
    attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Attachment',
        compute='_compute_attachment_id',
        store=True,
        ondelete='cascade',
        copy=False,
    )
    filename = fields.Char()
    comment = fields.Text(string='Comment')
    order_line = fields.One2many(
        string='Products',
        comodel_name='purchase.order.line',
        inverse_name='date_arrival_id',
        domain="[('order_id', '=', order_id), ('date_arrival_id', '=', False), ('display_type', '=', False)]",
        copy=False,
    )
    price_unit_verified = fields.Boolean(
        string='Verified prices',
        default=False,
        help='Whether the product prices were confirmed by the seller '
             ' in acknowledgment and verified by someone.'
    )

    # @api.constrains('order_id', 'order_line')
    # def _constrain_order_consistency(self):
    #     for arrival in self:
    #         line_order_id = arrival.order_line.order_id
    #         if line_order_id and arrival.order_id and line_order_id != arrival.order_id:
    #             raise exceptions.ValidationError(_(
    #                 "The Purchase Order of the Vendor Acknowledgment should not be different "
    #                 "than the Purchase Order of the products (%s, %s)."
    #                 arrival.order_id.display_name,
    #                 line_order_id.mapped('display_name')
    #             ))
    
    #===== CRUD =====#
    @api.model_create_multi
    def create(self, vals_list):
        """ `ir.attachment`
            Don't store `ir_attachment`.`res_field` for `purchase.arrival.date` attachments
            because it throws an access error and we actually don't need it
        """
        res = super().create(vals_list)
        res.sudo().attachment_id.res_field = False # sudo() to bypass access error
        return res
    
    def unlink(self):
        """ Force the refresh of `purchase_order`.`date_arrival_state`
            because removal of `purchase.arrival.date` record
            doesn't trigger the recompute
        """
        order_ids = self.order_id
        res = super().unlink()
        order_ids._compute_date_arrival_state()
        return res

    #===== Onchange =====#
    @api.onchange('date_arrival')
    def _onchange_date_arrival(self):
        """ Real-time update of po lines `planned_date` in arrival form """
        for arrival in self:
            arrival.order_line.date_planned = arrival.date_arrival

    @api.onchange('order_id')
    def _onchange_order_id(self):
        """ When creating new acknowledgment form from scratch (not wizard),
            auto-fill order line
        """
        for arrival in self:
            arrival.order_line = arrival.order_id._get_unconfirmed_date_order_line()

    #===== Compute =====#
    @api.depends('filename')
    def _compute_attachment_id(self):
        res = self.env['ir.attachment'].search_read(
            domain=[
                ('res_model', '=', self._name),
                ('res_id', 'in', self.ids),
                ('res_field', '=', 'attachment')
            ],
            fields=['res_id']
        )
        mapped_attachments = {vals['res_id']: vals['id'] for vals in res}
        for arrival in self:
            arrival.attachment_id = mapped_attachments.get(arrival.id)
        
        self._update_attachment_name()

    def _update_attachment_name(self):
        """ Synchronize `filename` in `ir.attachment`,
            else filename is not well displayed when shown in `purchase.order` form
        """
        for arrival in self:
            arrival.attachment_id.name = (
                '[{}] {}' . format(arrival.date_arrival, arrival.filename) if arrival.filename
                else str(arrival.date_arrival)
            )

    #===== Button =====#
    def action_toggle_price_unit_verified(self):
        for arrival in self:
            arrival.price_unit_verified = not arrival.price_unit_verified
