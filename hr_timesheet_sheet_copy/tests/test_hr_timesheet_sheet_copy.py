# -*- coding: utf-8 -*-

from odoo import fields, exceptions
from odoo.tests.common import Form

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo.addons.hr_timesheet_sheet.tests.test_hr_timesheet_sheet import TestHrTimesheetSheetCommon


class TestHrTimesheetSheetCopy(TestHrTimesheetSheetCommon):
    def test_01_copy(self):
        # previous sheet
        sheet_form = Form(self.sheet_model.with_user(self.user))
        today = datetime.today()
        sheet_form.date_start = today - relativedelta(years=10, days=2)
        sheet_form.date_end = sheet_form.date_start + relativedelta(weeks=1)
        sheet = sheet_form.save()

        # copy: should not raise
        try:
            new_sheet = sheet.copy()
        except:
            self.fail('Sheet should be OK to copy if not date overlapping')
        
        self.assertTrue(new_sheet.date_start, self.sheet_model._default_date_start())
