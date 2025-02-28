# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HolidaysRequest(models.Model):
    _inherit = ["hr.leave"]

    employee_id = fields.Many2one(
        domain=lambda self: self._get_employee_ids_domain()
    )
    employee_ids = fields.Many2many(
        domain=lambda self: self._get_employee_ids_domain()
    )

    def _get_employee_ids_domain(self):
        if self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            return [(1, '=', 1)]
        else:
            return [('leave_manager_id', '=', self.env.user.employee_id.id)]
