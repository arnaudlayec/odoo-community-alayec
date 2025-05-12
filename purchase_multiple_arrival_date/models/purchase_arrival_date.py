# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class PurchaseArrivalDate(models.Model):
    _name = 'purchase.arrival.date'
    _description = 'Purchase Arrival Date'
    _rec_name = 'date_arrival'

    #===== Fields methods =====#
    def default_get(self, fields):
        """ Pre-fill `order_line` with remaining not-confirmed-yet lines """
        vals = super().default_get(fields)
        order = self.env['purchase.order'].browse(
            vals.get('order_id') or self._context.get('default_order_id')
        )
        if order and 'order_line' in fields:
            vals['order_line'] = [Command.set(order.order_line.filtered(
                lambda x: not x.date_arrival_id and not x.display_type
            ).ids)]
        return vals

    #===== Fields =====#
    order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        required=True,
        ondelete='cascade',
        help='Products on which the Arrival Date will apply. '
             'Pre-filled with yet unconfirmed products.'
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
    )
    filename = fields.Char()
    comment = fields.Text(string='Comment')
    order_line = fields.One2many(
        string='Products',
        comodel_name='purchase.order.line',
        inverse_name='date_arrival_id',
    )

    #===== CRUD =====#
    def unlink(self):
        self.order_line.date_arrival_confirmed = False
        return super().unlink()
    
    @api.model_create_multi
    def create(self, vals_list):
        """ Don't store `ir_attachment`.`res_field` for `purchase.arrival.date` attachments
            because it throws an access error and we actually don't need it
        """
        res = super().create(vals_list)
        # need sudo() to bypass access error
        res.sudo().attachment_id.res_field = False
        return res

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
