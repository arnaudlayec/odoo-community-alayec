# -*- coding: utf-8 -*-

from odoo import api, models, fields, exceptions, _

class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ['stock.picking', 'project.default.mixin']

    #===== Fields methods =====#
    def default_get(self, fields):
        vals = super().default_get(fields)
        group_id = self.group_id or self.env['procurement.group'].browse(vals.get('group_id'))
        if 'project_id' in vals and group_id:
            vals['project_id'] = self._default_project_id(group_id).id
        return vals
    
    def _default_project_id(self, group_id=None):
        group_id = group_id or self.group_id
        project = self.mrp_production_ids.project_id
        return len(project) == 1 and project

    #===== Fields =====#
    project_id = fields.Many2one(
        # can be set manually or computed from the MO (via the procurement group)
        compute='_compute_project_id',
        store=True,
        readonly=False
    )
    mrp_production_ids = fields.One2many(
        related='group_id.mrp_production_ids'
    )

    #===== Compute =====#
    @api.depends('mrp_production_ids', 'mrp_production_ids.project_id')
    def _compute_project_id(self):
        """ Automatic project value from a MO (or a PO) via the procurement group """
        for picking in self:
            if picking.mrp_production_ids:
                picking.project_id = picking._default_project_id()
