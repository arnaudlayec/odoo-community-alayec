# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class StockMove(models.Model):
    _inherit = ['stock.move']

    comment = fields.Char(string='Comment')
