# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ["project.task"]

    attachment_ids = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name='res_id',
        string='Attachments',
        domain=[('res_model', '=', _name)],
    )
