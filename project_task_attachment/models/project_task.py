# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = ["project.task"]

    attachment_ids = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name='res_id',
        string='Attachments',
        domain=lambda self: [('res_model', '=', self._name)],
    )
