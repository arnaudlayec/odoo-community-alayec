# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command

class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "project.default.mixin"]

    project_id = fields.Many2one(
        # pre-selected favorite project on new task, but let the field not required
        required=False,
        # There are a lot views of `project.task` with `project_id`, including from `hr_timesheet`
        # The `project_id_domain` must be added to each of these view so the domain of
        #  `project_id` works, which is difficult to do and maintain
        # => Let's update 1-by-1 via XML the domain of `project_id` in views where this feature
        #  is wanted
        domain=[]
    )
