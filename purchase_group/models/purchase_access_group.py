#  @author: Alexis de Lattre <alexis.delattre@akretion.com>

from odoo import models, fields, api


class PurchaseAccessGroup(models.Model):
    _name = 'purchase.access.group'
    _description = 'ACL for PO and supplier invoices'
    _order = 'sequence, id'

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, string='Group name')
    user_ids = fields.Many2many('res.users', string='Members')
    description = fields.Html(string='Description')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company
    )
