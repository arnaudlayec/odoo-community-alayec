# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class HrEmployeeBase(models.AbstractModel):
    _inherit = ['hr.employee.base']

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        help="If empty, follows department's"
    )

    def _get_analytic_account_id(self):
        return self.analytic_account_id or self.department_id.analytic_account_id
