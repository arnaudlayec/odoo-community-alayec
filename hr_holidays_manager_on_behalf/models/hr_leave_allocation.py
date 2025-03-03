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
