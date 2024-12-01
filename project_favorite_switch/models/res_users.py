# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Users(models.Model):
    _inherit = ["res.users"]

    favorite_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Favorite project',
    )
    
    def _refresh_favorite_project_id(self):
        """ Called from `project.project`
            Sets `favorite_project_id` when user has a single favorite project
        """
        domain = [
            ('favorite_user_ids', '=', self.env.uid),
            ('stage_id.fold', '=', False), # filter finished projects
        ]
        project_ids = self.env['project.project'].search(domain)
        self.favorite_project_id = fields.first(project_ids).id if len(project_ids) == 1 else False
