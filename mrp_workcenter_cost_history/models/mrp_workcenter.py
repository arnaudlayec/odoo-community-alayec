# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkcenter(models.Model):
    _inherit = ["mrp.workcenter"]

    cost_history_ids = fields.One2many(
        comodel_name="hr.employee.timesheet.cost.history",
        inverse_name="workcenter_id",
        copy=False,
    )
    workorder_ids = fields.One2many(
        comodel_name='mrp.workorder',
        inverse_name='workcenter_id',
        string='Work Orders',
    )
