# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

class ProjectWizard(models.TransientModel):
    _name = "project.choice.wizard"
    _description = "Project Choice"
    _inherit = ['project.default.mixin']

    def button_validate(self):
        """ Called from wizzard """
        return self.action_choose_project_and_redirect(
            self._context.get('action_arg'),
            self._context.get('context_keys')
        )

    def action_choose_project_and_redirect(self, action_arg, context_keys=None):
        """ To call from a server action attached to a menuitem
            
            :args:
                `action_arg` is either:
                - a string (XMLID) of the original action to open
                - or a callable function taking a `project.project` record as single arg and returning
                a dict of a full custom action
                
                `context_keys` allow to customize the context keys to fill in with `project_id`
                and is similarly either a list of keys or a callable
            
            :return:
                An action's dict, either:
                 (a) the requested action in `action_arg`, if the project is guessable from user or context
                 (b) else, a wizard to chose 1 project, which then opens (a)
                In both case, the action's `context` and `domain` is extended with project-related data.
        """

        # If project can't be guessed, open the project-choice wizard
        project_id_ = self.env['project.default.mixin']._get_project_id()
        context_keys = context_keys or self._context # if not explicit, transmit current context
        if not project_id_:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.choice.wizard',
                'view_mode': 'form',
                'name': 'Choose a project',
                'context': {'action_arg': action_arg, 'context_keys': context_keys},
                'target': 'new'
            }
        
        # Get and customize the action to return
        project_id = self.env['project.project'].browse(project_id_)
        action = self._get_action(project_id, action_arg)
        action = self._automate_context_and_domain(project_id, action, context_keys, action_arg)
        return action
    
    def _get_action(self, project_id, action_arg):
        # When project is known, compute and return action to open final-requested view
        if callable(action_arg): # a custom action
            return action_arg(project_id)
        else: # `action` is an XMLID
            return self.env['ir.actions.act_window']._for_xml_id(action_arg)
    
    def _automate_context_and_domain(self, project_id, action, context_keys, action_arg=None):
        # Update context
        context_keys = context_keys or ['default_project_id']
        if callable(context_keys):
            action['context'] = context_keys(project_id)
        else:
            action['context'] = (
                action.get('context', {})
                | {key: project_id.id for key in context_keys}
            )
        
        # Update domain
        domain = safe_eval(action.get('domain') or '[]')
        action['domain'] = expression.AND([
            domain,
            [('project_id', '=', project_id.id)]
        ])
        return action
