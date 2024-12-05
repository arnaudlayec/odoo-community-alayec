# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

class HrTimesheetSheet(models.Model):
    _inherit = ['hr_timesheet.sheet']

    date_start = fields.Date(
        copy=False # recalculate default when copying
    )
    date_end = fields.Date(
        copy=False # recalculate default when copying
    )

    @api.model
    def copy(self, default=None):
        """ Allow copying any sheet into the default `current period` sheet """
        self = self.with_context(allow_copy_timesheet = True)
        return super(HrTimesheetSheet, self).copy(default)
    