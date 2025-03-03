# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HolidaysRequest(models.Model):
    """ Adds accesses for Time Off responsible of employees so they may manage leaves on
         behalf on their subordinates. They may:
         - create leaves
         - see name field
    """
    _inherit = ["hr.leave"]

    #===== Fields' domain =====#
    def _get_subordinates_or_all(self):
        domain = self._get_subordinates_or_all_domain()
        return self.env['hr.employee'].search(domain)
    def _get_subordinates_or_all_domain(self):
        """ Domain for:
            1. all employees if *group_hr_holidays_user*
            2. subordinates if *group_hr_holidays_responsible*
        """
        return (
            [(1, '=', 1)] if self.env.user.has_group('hr_holidays.group_hr_holidays_user')
            else [('leave_manager_id', '=', self.env.uid)]
        )
    
    #===== Fields =====#
    employee_id = fields.Many2one(
        domain="[('id', 'in', employee_ids_possible)]"
    )
    employee_ids = fields.Many2many(
        groups="hr_holidays.group_hr_holidays_responsible",
        domain="[('id', 'in', employee_ids_possible)]"
    )
    all_employee_ids = fields.Many2many(
        search='_search_all_employee_ids',
    )
    employee_ids_possible = fields.Many2many(
        comodel_name='hr.employee',
        default=_get_subordinates_or_all,
        store=False
    )
    
    #===== Compute =====#
    def _search_all_employee_ids(self, operator, value):
        if hasattr(value, '__iter__'):
            return [('employee_ids', operator, value)]
        else:
            return [('employee_id', operator, value)]

    #===== Name/Description =====#
    @api.depends_context('uid')
    def _compute_description(self):
        """ Also allow Time Off responsible to handle leaves' name """
        super()._compute_description()

        subordinates_leaves = self.filtered(lambda x: x.employee_ids.leave_manager_id == self.env.user)

        for leave in subordinates_leaves:
            leave.name = leave.sudo().private_name

    def _inverse_description(self):
        super()._inverse_description()
        
        subordinates_leaves = self.filtered(lambda x: x.employee_ids.leave_manager_id == self.env.user)

        for leave in subordinates_leaves:
            leave.sudo().private_name = leave.name

    def _search_description(self, operator, value):
        domain = [('private_name', operator, value), ('leave_manager_id', '=', self.env.user.id)]
        return super()._search_description() | self.search(domain)
