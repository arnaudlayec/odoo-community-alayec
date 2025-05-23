# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseProjectDiscount(models.Model):
    _name = 'purchase.project.discount'
    _inherit = ['project.default.mixin']
    _description = 'Purchase Project Discount'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        string='Vendor',
        comodel_name='res.partner',
        domain=[('parent_id', '=', False)],
        ondelete='cascade',
        required=True,
    )
    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
    )
    contract_ref = fields.Char(
        string='Contract Reference',
        help='Reference of discount agreement, displayed on printed Purchase Order.',
    )

    _sql_constraints = [
        (
            "discount_limit",
            "CHECK (discount <= 100.0)",
            "Discount must be lower than 100%.",
        ), (
            "partner_project_id",
            "UNIQUE (project_id, partner_id)",
            "A vendor may have only 1 discount per project."
        )
    ]
