# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = ["hr.employee"]

    def _attendance_action(self, next_action):
        """ Called after:
            - Badge scan
            - PIN Code
            - Button 'Identity manually + Click on hr.employee.public Kanban card + Check IN button'
        """
        if self.manufacturing_worker:
            return self._action_mrp_attendance()
        else:
            return super()._attendance_action(next_action)
