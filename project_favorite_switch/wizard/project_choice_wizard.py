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

    def action_choose_project_and_redirect(self, action_arg, context_keys=['default_project_id']):
        """ To call from a server action attached to a menuitem
            :arg action_arg: is either:
                - a string (XMLID) of the original action to open
                - or a dict of a custom action
            :option context_keys: list of context keys to receive `project_id_` as value

            :return: An action's dict, either:
                 (a) the requested action in `action`, if the project is guessable from user or context
                 (b) else, a wizard to chose 1 project, which then opens (a)
                In both case, the action's `context` and `domain` is extended with project-related data.
        """
        # Let's try to fetch project all possible way
        project_id = self.project_id or self.env['project.project'].browse(self._get_project_id())

        # If project is guessable or was choosen from wizard: open the target action
        if project_id.id:
            action = self._automate_context_and_domain(project_id, context_keys, (
                action_arg if isinstance(action_arg, dict)
                else self.env['ir.actions.act_window']._for_xml_id(action_arg)
            ))
        
        # If project can't be guessed, open the project-choice wizard
        else:
            action = {
                'type': 'ir.actions.act_window',
                'res_model': 'project.choice.wizard',
                'view_mode': 'form',
                'name': 'Choose a project',
                'context': self._context | {'action': action_arg, 'context_keys': context_keys},
                'target': 'new'
            }
        return action
    
    
    def _automate_context_and_domain(self, project_id, context_keys, action_dict):
        """ When project is known, add relevant keys
            in `context` and part in `domain`

            note: both action_dict['context'] and action_dict['domain'] can be str or python object
            depending `action_arg` was a dict or a XML_ID
        """
        # Prefix action's name with project's
        action_dict['name'] = '{} / {}' . format(project_id.display_name, action_dict['name'])

        # Update context to add project's default keys
        context = action_dict.get('context')
        context = safe_eval(context) if isinstance(context, str) else context or {}
        action_dict['context'] = (
            self._context
            | context
            | {'action_origin': action_dict.copy()}
            | {key: project_id.id for key in context_keys}
        )
        
        # Domain: get existing
        domain = action_dict.get('domain')
        domain = safe_eval(domain) if isinstance(domain, str) else domain or []
        # Update domain to filter on selected project
        action_dict['domain'] = expression.AND([
            domain,
            [('project_id', '=', project_id.id)]
        ])
        return action_dict
