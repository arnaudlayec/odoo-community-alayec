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
        fav_projects = self._get_favorite_projects()
        self.favorite_project_id = fields.first(fav_projects).id if len(fav_projects) == 1 else False

    def _get_favorite_projects(self):
        Project = self.env['project.project']
        return Project.search(Project._get_domain_fav_projects())
