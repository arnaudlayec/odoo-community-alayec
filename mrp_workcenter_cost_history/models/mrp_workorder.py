# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkorder(models.Model):
    _inherit = ["mrp.workorder"]

    def _create_or_update_analytic_entry(self):
        """ Overwrites costs sum in analytic line following costs history """
        super()._create_or_update_analytic_entry()

        for wo in self:
            wo.mo_analytic_account_line_id.amount = sum(wo.time_ids.mapped('cost'))
            wo.wc_analytic_account_line_id.amount = sum(wo.time_ids.mapped('cost'))
