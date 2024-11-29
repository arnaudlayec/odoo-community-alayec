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
        # (!) NON-FOLDED projects in user's favorites,
        # thus not exactly the reverse field of `project_project.favorite_user_ids`
        comodel_name='project.project',
        inverse_name='favorite_user_ids',
        string='Favorite projects',
        readonly=True,
        domain=[('stage_id.fold', '=', False)]
    )
    
    @api.depends('favorite_project_ids')
    def _computed_favorite_project_id(self):
        for user in self:
            user.favorite_project_id = user.favorite_project_ids.ids[0] if len(user.favorite_project_ids) == 1 else False
