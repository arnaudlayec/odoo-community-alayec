# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HolidaysAllocation(models.Model):
    _inherit = ["hr.leave.allocation"]

    employee_id = fields.Many2one(
        domain=lambda self: self.env['hr.leave']._get_employee_ids_domain()
    )
    employee_ids = fields.Many2many(
        domain=lambda self: self.env['hr.leave']._get_employee_ids_domain()
    )
    