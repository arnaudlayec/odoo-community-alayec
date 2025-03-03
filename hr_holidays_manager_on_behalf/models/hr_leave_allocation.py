# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HolidaysAllocation(models.Model):
    _inherit = ["hr.leave.allocation"]

    employee_id = fields.Many2one(domain="[('id', 'in', employee_ids_domain)]")
    employee_ids = fields.Many2many(domain="[('id', 'in', employee_ids_domain)]")
    employee_ids_domain = fields.Many2many(compute='_compute_employee_ids_domain')

    def _compute_employee_ids_domain(self):
        domain = self.env['hr.leave']._get_employee_ids_domain()
        self.employee_ids_domain = self.env['hr.employee'].search(domain)
