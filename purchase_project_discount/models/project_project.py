# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = ['project.project']

    purchase_discount_ids = fields.One2many(
        string='Discounts',
        comodel_name='purchase.project.discount',
        inverse_name='project_id',
    )
