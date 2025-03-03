# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HolidaysAllocation(models.Model):
    _inherit = ["hr.leave.allocation"]

    employee_id = fields.Many2one(domain="[('id', 'in', employee_ids_possible)]")
    employee_ids = fields.Many2many(domain="[('id', 'in', employee_ids_possible)]")
    employee_ids_possible = fields.Many2many(
        comodel_name='hr.employee',
        default=lambda self: self.env['hr.leave']._get_subordinates_or_all(),
        store=False
    )
