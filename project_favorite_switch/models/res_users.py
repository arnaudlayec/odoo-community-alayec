# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Users(models.Model):
    _inherit = ["res.users"]

    favorite_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Favorite project',
        compute='_computed_favorite_project_id',
        store=True
    )
    favorite_project_ids = fields.One2many(
        # reverse field of `project_project.favorite_user_ids`
        comodel_name='project.project',
        inverse_name='favorite_user_ids',
        string='Favorite projects',
        readonly=True
    )
    
    @api.depends('favorite_project_ids')
    def _computed_favorite_project_id(self):
        mapped_favorite_project_ids = {
            x.user_id.id: x.ids
            for x in self.favorite_project_ids.filtered_domain([('stage_id.fold', '=', False)])
        }
        for user in self:
            project_ids_ = mapped_favorite_project_ids.get(user.id, [])
            user.favorite_project_id = project_ids_[0] if len(project_ids_) == 1 else False
