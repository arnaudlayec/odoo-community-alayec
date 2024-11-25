# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _

class ProjectProject(models.Model):
    _inherit = "project.project"

    privacy_visibility = fields.Selection(default='followers')

    #===== CRUD (assignees/followers synch) =====#
    def write(self, vals):
        """ If project's privacy is moved to `followers`,
            rebase project's followers from roles
        """
        if self._should_synch_roles(vals):
            internal_followers = self.message_partner_ids.filtered(lambda x: x.user_id.id)
            assignees = self.assignment_ids._filter_has_access().user_id.partner_id
            # unsubscribe all internal users not assigned to roles as primary
            # subscribe those last ones
            self.message_unsubscribe((internal_followers - assignees).ids)
            self.message_subscribe(assignees.ids)
        return super().write(vals)
    def _should_synch_roles(self, vals=None):
        """ Can be overriden to change logic on `privacy_visibility` """
        privacy = vals.get('privacy_visibility') if vals else self.privacy_visibility
        return privacy == 'followers'
    
    #===== Constrain (assignees/followers synch) =====
    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        """ Can't add internal users to followers if not primary assignees """
        user_ids = self.sudo().env['res.partner'].browse(partner_ids).user_ids
        if user_ids.ids:
            assignee_ids = self.assignment_ids._filter_has_access().user_id.ids
            if any([x not in assignee_ids for x in user_ids.ids]):
                self._raise_followers_error()
        return super().message_subscribe(partner_ids, subtype_ids)
    
    def message_unsubscribe(self, partner_ids=None):
        """ Can't remove internal users from followers
            if they are primary assignees
        """
        assignees_ids_ = self.assignment_ids._filter_has_access().user_id.partner_id.ids
        if any([x in assignees_ids_ for x in partner_ids]):
            self._raise_followers_error()
        
        return super().message_unsubscribe(partner_ids)
    
    def _raise_followers_error(self):
        if self._should_synch_roles() and not self._context.get('unsubscribe_no_raise'):
            raise exceptions.ValidationError(_(
                "To (un)subscribe internal users to the projet,"
                " please (un)assign them to project Roles."
            ))
