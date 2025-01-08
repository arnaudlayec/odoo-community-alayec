# -*- coding: utf-8 -*-

from odoo import api, models, fields, exceptions, _

class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ['stock.picking', 'project.default.mixin']

    project_id = fields.Many2one(
        # can be set manually or computed from procurment group
        compute='_compute_project_id',
        store=True,
        readonly=False
    )

    @api.depends('group_id.project_id')
    def _compute_project_id(self):
        """ Automatic project value from a MO (or a PO) via the procurement group """
        for picking in self:
            picking.project_id = group_id.project_id
