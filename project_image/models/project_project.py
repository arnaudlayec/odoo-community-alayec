# -*- coding: utf-8 -*-

from odoo import models

class Project(models.Model):
    _name = "project.project"
    _inherit =["project.project", "image.mixin"]
