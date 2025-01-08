# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

class ProcurementGroup(models.Model):
    _inherit = ['procurement.group']

    project_id = fields.Many2one(
        # can be set from PO or MO, or by user from the picking
        comodel_name='project.project',
        string='Project',
        compute='_compute_project_id',
        store=True,
        readonly=False
    )

    @api.onchange('stock_move_ids.picking_id.project_id')
    def _compute_project_id(self):
        """ User-entry: update procurement's group project from the picking """
        for group in self:
            project = group.stock_move_ids.picking_id.project_id
            group.project_id = len(project) == 1 and project
