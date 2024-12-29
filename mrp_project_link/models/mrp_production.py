# -*- coding: utf-8 -*-

from odoo import models, fields

class WorkOrder(models.Model):
    _name = "mrp.production"
    _inherit = ['mrp.production', 'project.default.mixin']
    _rec_name = 'display_name'

    description = fields.Char(
        string='Description'
    )
    
    def _compute_display_name(self):
        for mo in self:
            mo.display_name = '[{}] {}' . format(self.name, self.description) 
