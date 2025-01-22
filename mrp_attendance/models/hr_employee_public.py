# -*- coding: utf-8 -*-

from odoo import fields, models

class HrEmployeePublic(models.Model):
    _inherit = ['hr.employee.public']

    def action_employee_kiosk_confirm(self):
        """ We need to bypass `hr_attendance_kiosk_confirm` to fully re-write JS action
            See comment in `mrp_attendance/kiosk_confirm.js`
        """
        return super().action_employee_kiosk_confirm() | {
            'tag': 'mrp_attendance_kiosk_confirm',
        }
