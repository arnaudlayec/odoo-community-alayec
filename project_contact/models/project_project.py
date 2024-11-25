# -*- coding: utf-8 -*-

from odoo import models, fields

class Project(models.Model):
    _inherit = "project.project"

    contact_ids = fields.One2many('project.contact', 'project_id', string='Stakeholders')
