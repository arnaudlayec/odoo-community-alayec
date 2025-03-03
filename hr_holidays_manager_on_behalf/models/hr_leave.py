# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HolidaysRequest(models.Model):
    _inherit = ["hr.leave"]

    employee_id = fields.Many2one(domain="[('id', 'in', employee_ids_domain)]")
    employee_ids = fields.Many2many(
        groups="hr_holidays.group_hr_holidays_responsible",
        domain="[('id', 'in', employee_ids_domain)]"
    )
    employee_ids_domain = fields.Many2many(compute='_compute_employee_ids_domain')

    def _compute_employee_ids_domain(self):
        domain = self._get_employee_ids_domain()
        self.employee_ids_domain = self.env['hr.employee'].search(domain)
    
    def _get_employee_ids_domain(self):
        return (
            [(1, '=', 1)] if self.env.user.has_group('hr_holidays.group_hr_holidays_user')
            else [('leave_manager_id.user_id', '=', self.env.uid)]
        )
