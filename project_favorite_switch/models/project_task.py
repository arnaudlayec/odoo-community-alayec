# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command

class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "project.default.mixin"]

    project_id = fields.Many2one(
        # pre-selected favorite project on new task, but let the field not required
        required=False
    )