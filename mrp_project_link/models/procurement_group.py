# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

class ProcurementGroup(models.Model):
    _inherit = ['procurement.group']

    project_id = fields.Many2one(
        # can be set from PO or MO
        comodel_name='project.project',
        string='Project'
    )
