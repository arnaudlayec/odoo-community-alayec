# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    _inherit = ['account.analytic.account']

    timesheetable = fields.Boolean(
        string='Timesheetable?',
        default=False
    )

    def name_get(self):
        """ Adds clock char icon in display_name if marked as `timesheetable` """
        res = super().name_get()
        return [
            (id_, name + ' 🕓' if self.browse(id_).timesheetable else '')
            for id_, name in res
        ]
