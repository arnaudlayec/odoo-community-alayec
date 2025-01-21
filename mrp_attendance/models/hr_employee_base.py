# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployeeBase(models.AbstractModel):
    _inherit = ["hr.employee.base"]

    manufacturing_worker = fields.Boolean(
        string='Manufacturing Worker',
        help='If activated, this Employee only sees other Manufacturing Workers from the Presence app '
            ' (in Kiosk display) and she/he is redirected to the Manufacturing app to log its productivity'
            ' times instead of Check IN / Check OUT attendance buttons.',
        compute='_compute_manufacturing_worker',
        search='_search_manufacturing_worker',
    )

    #===== Compute =====#
    @api.depends('user_id', 'user_id.groups_id')
    def _compute_manufacturing_worker(self):
        mf_workers = self._get_mf_workers()
        for employee in self:
            employee.manufacturing_worker = employee.user_id in mf_workers

    @api.model
    def _search_manufacturing_worker(self, operator, value):
        return [('user_id', 'in', self._get_mf_workers().ids)]
    
    def _get_mf_workers(self):
        return (
            self.env.ref('mrp_attendance.group_hr_attendance_mrp').users
            - self.env.ref('hr_attendance.group_hr_attendance').users
        )
    
    #===== Business Logics =====#
    def _action_mrp_attendance(self):
        """ Returns the actions to skip attendance's Check IN / Check OUT workflow
            and redirects to Manufacturing Times instead
        """
        if not self.user_id:
            # (!) mrp.workcenter.productivity logs `user_id`, not `employee_id`
            # we don't override this method because it extends to some other feature
            # like mrp_workerorder.working_user_ids
            raise exceptions.UserError(_(
                'Your profile must be linked to an active user to use Manufacturing Attendance.'
                ' Please contact your Human Resources to change this settings.'
            ))
        
        return {
            'action': {
                'name': _('Manufacturing Orders'),
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'views': [(self.env.ref('mrp_attendance.mrp_production_kanban_view_attendance').id, 'kanban')],
                'search_view_id': [self.env.ref('mrp_attendance.view_mrp_production_filter_attendance').id],
                'context': self._context | {
                    'mrp_attendance_user_id': self.user_id.id,
                    'workorder_display_name_simple': 1
                },
                'domain': self.env['mrp.production']._get_domain_mo_attendance(),
            }
        }
