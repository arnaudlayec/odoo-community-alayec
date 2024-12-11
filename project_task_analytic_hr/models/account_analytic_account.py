# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    _inherit = ['account.analytic.account']

    timesheetable = fields.Boolean(
        string='Timesheetable?',
        default=False
    )

    def _compute_display_name(self):
        """ Adds clock char icon in display_name if marked as `timesheetable` """
        super()._compute_display_name()
        for analytic in self:
            analytic._compute_display_name_one()
    
    def _compute_display_name_one(self):
        self.ensure_one()
        if self.timesheetable:
            self.display_name += ' 🕓'
