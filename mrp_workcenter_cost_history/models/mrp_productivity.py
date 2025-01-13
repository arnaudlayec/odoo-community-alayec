# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkcenterProductivity(models.Model):
    _inherit = ["mrp.workcenter.productivity"]

    costs_hour = fields.Monetary(
        string='Hour cost',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """ Log workcenter cost at the time of the timesheet """
        
        workcenter_ids = [x['workcenter_id'] for x in vals_list]
        workcenters = self.env['mrp.workcenter'].browse(workcenter_ids)
        for vals in vals_list:
            vals['costs_hour'] = workcenters.browse(vals['workcenter_id']).costs_hour
        
        return super().create(vals_list)
