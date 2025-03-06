# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _

class ProjectProject(models.Model):
    _inherit = ["project.project"]

    privacy_visibility = fields.Selection(default='followers')

    #===== CRUD (assignees/followers synch) =====#
    def copy(self, default={}):
        """ If project's privacy is `followers`,
            synchronize project's followers from roles assignments
        """
        if self._should_synch_roles(default):
            self = self.with_context(project_role_no_raise=True)
        
        return super(ProjectProject, self).copy(default)._rebase_followers_from_assignments()
    
    def write(self, vals):
        """ If project's privacy is moved to `followers`,
            rebase project's followers from roles assignments
        """
        if 'privacy_visibility' in vals:
            self._rebase_followers_from_assignments(vals)
        return super().write(vals)
    
    def _rebase_followers_from_assignments(self, vals={}):
        """ For elligible projects:
            1. Unsubscribe all internal users not assigned to roles
            2. Subscribe those last ones
        """
        if not self._should_synch_roles(vals):
            return
        
        for project in self.with_context(project_role_no_raise=True):
            internal_followers = project.message_partner_ids.filtered(lambda x: x.user_id.id)
            assignees = project.assignment_ids._filter_has_access().user_id.partner_id
            project.message_unsubscribe((internal_followers - assignees).ids)
            project.message_subscribe(assignees.ids)
    
    def _should_synch_roles(self, vals={}):
        """ Can be overriden to change logic on `privacy_visibility` """
        privacy = vals.get('privacy_visibility', self.privacy_visibility)
        return privacy == 'followers'
    
    #===== Constrain (assignees/followers synch) =====
    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        """ Can't add internal users to followers if not assignees """
        user_ids = self.sudo().env['res.partner'].browse(partner_ids).user_ids
        if user_ids.ids:
            assignee_ids = self.assignment_ids._filter_has_access().user_id.ids
            if any([x not in assignee_ids for x in user_ids.ids]):
                self._raise_followers_error()
        return super().message_subscribe(partner_ids, subtype_ids)
    
    def message_unsubscribe(self, partner_ids=None):
        """ Can't remove internal users from followers
            if they assignees
        """
        assignees_ids_ = self.assignment_ids._filter_has_access().user_id.partner_id.ids
        if any([x in assignees_ids_ for x in partner_ids]):
            self._raise_followers_error()
        
        return super().message_unsubscribe(partner_ids)
    
    def _raise_followers_error(self):
        if self._should_synch_roles() and not self._context.get('project_role_no_raise'):
            raise exceptions.ValidationError(_(
                "To (un)subscribe internal users to the projet,"
                " please (un)assign them to project Roles."
            ))
    
    #===== Business methods =====#
    def _get_user_role_ids(self, user_id=None):
        """ Returns user's roles on a given project """
        user_id = user_id or self.env.user
        domain = [('project_id', '=', self.id), ('user_id', '=', user_id.id)]
        return self.env['project.assignment'].search(domain).role_id
