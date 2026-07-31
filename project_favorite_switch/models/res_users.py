# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Users(models.Model):
    _inherit = ["res.users"]

    favorite_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Favorite project',
    )

    def write(self, vals):
        """When project user/admin rights changes, refresh the
        `favorite_project_id` to prevent access errors"""
        res = super().write(vals)
        if (
            set(vals).intersection({"groups_id", "role_line_ids"})
            and self.env.user.has_group("project.group_project_user")
        ):
            self._refresh_favorite_project()
        return res

    def _refresh_favorite_project(self):
        """ Called from `project.project`
            Sets `favorite_project_id` when user has a single favorite project
        """
        if self._context.get("refresh_favorite_project"): # prevent infinite loop
            return
        self = self.with_context(refresh_favorite_project=1)

        fav_projects = self._get_favorite_projects()
        self.favorite_project_id = len(fav_projects) == 1 and fav_projects

    def _get_favorite_projects(self):
        ProjectUser = self.env['project.project'].with_user(self)
        return ProjectUser.search([("is_favorite", "=", True)])
