# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class HrDepartment(models.Model):
    _inherit = ['hr.department']

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        help='Will defined the Analytic Account of the Tasks created by'
             ' the employees of the department.'
    )
