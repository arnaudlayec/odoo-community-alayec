# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = ["project.task"]

    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string='Attachments',
        store=True,
        compute=False
    )
