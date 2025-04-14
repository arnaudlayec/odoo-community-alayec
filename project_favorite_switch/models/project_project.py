# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command
from odoo.osv import expression

class ProjectProject(models.Model):
    _inherit = ["project.project"]

    def _get_domain_fav_projects(self, fav_only=True):
        """ Can be overwritten or called by other models """
        return [
            ('company_id', '=', self.env.company.id),
            ('stage_id.fold', '=', False)
        ] + (
            [('favorite_user_ids', '=', self.env.uid)] if fav_only else []
        )

    #===== Fields =====
    is_favorite = fields.Boolean(search='_search_is_favorite')

    #===== Compute: Refresh `res_users.favorite_project_id` ======
    def _search_is_favorite(self, operator, value):
        if operator == '==' and value or operator == '!=' and not value:
            new_operator = 'in'
        else:
            new_operator = 'not in'
        
        domain = [('favorite_user_ids', '=', self.env.uid)]
        projects = self.env['project.project'].search(domain)
        return [('id', new_operator, projects.ids)]

    def _inverse_is_favorite(self):
        res = super()._inverse_is_favorite()
        self.env.user._refresh_favorite_project_id()
        return res

    def toggle_favorite(self):
        res = super().toggle_favorite()
        self.env.user._refresh_favorite_project_id()
        return res
    
    def toggle_active(self):
        res = super().toggle_active()
        self.favorite_user_ids._refresh_favorite_project_id()
        return res
    
    #===== Logic =====#
    # Add/remove a project to users' favorite when
    # users are added/removed to/from Chatter followers list
    # (very useful in combination with `project_role_visibility`)
    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        """ Add project to users' favorite when they subscribe to project's chatter """
        user_ids = self.sudo().env['res.partner'].browse(partner_ids).user_ids
        self.sudo().favorite_user_ids = [Command.link(x) for x in user_ids.ids]

        return super().message_subscribe(partner_ids, subtype_ids)
    
    def message_unsubscribe(self, partner_ids=None):
        """ Remove project to users' favorite when they unsubscribe to project's chatter """
        user_ids = self.sudo().env['res.partner'].browse(partner_ids).user_ids
        self.sudo().favorite_user_ids = [Command.unlink(x) for x in user_ids.ids]

        return super().message_unsubscribe(partner_ids)    
