# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = ['product.product']

    project_ids = fields.Many2many(
        comodel_name='project.project',
        relation='product_product_project_rel',
        column1='product_id',
        column2='project_id',
        string='Projects',
        help='Projects having stock moves with this product',
        compute='_compute_project_ids',
        store=True,
    )

    @api.depends('stock_move_ids', 'stock_move_ids.project_id')
    def _compute_project_ids(self):
        for product in self:
            product.project_ids = product.stock_move_ids.project_id
