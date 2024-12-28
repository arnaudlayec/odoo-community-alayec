# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

class Project(models.Model):
    _inherit = ["project.project"]

    manufacturing_order_count = fields.Integer(
        string="Manufacturing Orders",
        compute='_compute_manufacturing_order_count'
    )

    def _compute_manufacturing_order_count(self):
        rg_result = self.env['mrp.production'].sudo().read_group(
            domain=[('project_id', 'in', self.ids)],
            fields=['manufacturing_order_count:count(id)'],
            groupby=['project_id']
        )
        mapped_count = {x['project_id'][0]: x['manufacturing_order_count'] for x in rg_result}
        for project in self:
            project.manufacturing_order_count = mapped_count.get(project.id, 0)
