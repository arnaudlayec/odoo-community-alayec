# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaskType(models.Model):
    _inherit = ["project.task.type"]

    project_ids = fields.Many2many(
        required=False
    )
