# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

class ProjectWizard(models.TransientModel):
    _name = "project.choice.wizard"
    _description = "Project Choice"
    _inherit = ['project.default.mixin']
    
    def button_validate(self):
        """ Called from wizzard or `onchange` """
        return self.action_choose_project_and_redirect(
            self._context.get('action'),
            self._context.get('context_keys')
        )

    def action_choose_project_and_redirect(self, action, context_keys=['default_project_id']):
        """ To call from a server action attached to a menuitem
            :arg action: is either:
                - a string (XMLID) of the original action to open
                - or a dict of a custom action
            :option context_keys: list of context keys to receive `project_id_` as value

            :return: An action's dict, either:
                 (a) the requested action in `action`, if the project is guessable from user or context
                 (b) else, a wizard to chose 1 project, which then opens (a)
                In both case, the action's `context` and `domain` is extended with project-related data.
        """
        # Let's try to fetch project all possible way
        project_id = self.project_id
        if not project_id.id:
            project_id = self.env['project.project'].browse(self._get_project_id())

        # If project is guessable or was choosen from wizard: open the target action
        if project_id.id:
            action = self._automate_context_and_domain(project_id, context_keys, (
                action if isinstance(action, dict)
                else self.env['ir.actions.act_window']._for_xml_id(action)
            ))
        
        # If project can't be guessed, open the project-choice wizard
        else:
            action = {
                'type': 'ir.actions.act_window',
                'res_model': 'project.choice.wizard',
                'view_mode': 'form',
                'name': 'Choose a project',
                'context': self._context | {'action': action, 'context_keys': context_keys},
                'target': 'new'
            }
        return action
    
    
    def _automate_context_and_domain(self, project_id, context_keys, action):
        """ When project is known, add relevant keys
            in `context` and part in `domain`
        """
        # Prefix action's name with project's
        action['name'] = '{} / {}' . format(project_id.display_name, action['name'])

        # Update context to add project's default keys
        action['context'] = (
            action.get('context', {})
            | {key: project_id.id for key in context_keys}
        )
        
        # Domain: get existing
        domain = action.get('domain')
        domain = safe_eval(action['domain']) if isinstance(domain, str) else domain or []
        # Update domain to filter on selected project
        action['domain'] = expression.AND([
            domain,
            [('project_id', '=', project_id.id)]
        ])
        return action
