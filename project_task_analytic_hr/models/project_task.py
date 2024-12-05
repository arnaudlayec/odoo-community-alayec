# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

from collections import defaultdict

class Task(models.Model):
    _inherit = ['project.task']

    #===== Fields methods =====#
    @api.model
    def default_get(self, default_fields):
        """ By default, Task analytic follow project's
            **Enforce** this to follow Employee's analytic (if defined), no matter
             any other default `analytic_account_id` 
        """
        vals = super().default_get(default_fields)

        if 'analytic_account_id' in default_fields:
            analytic_id = self.env.user.employee_id._get_analytic_account_id().id
            if analytic_id:
                vals['analytic_account_id'] = analytic_id
        
        return vals
