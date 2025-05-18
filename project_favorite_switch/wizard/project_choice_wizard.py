# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


def _resolve_string_to_python(string):
    return safe_eval(string) if isinstance(string, str) else string or {}


class ProjectWizard(models.TransientModel):
    _name = "project.choice.wizard"
    _description = "Project Choice"
    _inherit = ['project.default.mixin']


    #===== Logics =====#
    def button_validate(self):
        """ Called from wizzard or `onchange` """
        return self.action_choose_project_and_redirect(
            self._context.get('action_arg'),
            self._context.get('context_keys')
        )

    def action_choose_project_and_redirect(self, action_arg, context_keys=['default_project_id']):
        """ To call from a server action attached to a menuitem
            :arg action_arg: is either:
                1. or a dict of a custom action
                2. a string of a method of `project.project` returning an action dict, like a
                   `button_...`
                3. a string (XMLID) of the original action to open
            :option context_keys: list of context keys to receive `project_id_` as value

            :return: An action's dict, either:
                 (a) the requested action in `action_arg`, if the project is guessable from user or context
                 (b) else, a wizard to chose 1 project, which then opens (a)
                In both case, the action's `context` and `domain` is extended with project-related data.
        """
        # Let's try to fetch project all possible way
        project_id = self.project_id or self.env['project.project'].browse(self._get_project_id())

        # If project is guessable or was choosen from wizard: open the target action
        if project_id.id:
            action = self._automate_context_and_domain(project_id, context_keys, action_arg)
            action['target'] = 'main' # clears breadcrumb
        
        # If project can't be guessed, open the project-choice wizard
        else:
            action = {
                'type': 'ir.actions.act_window',
                'res_model': 'project.choice.wizard',
                'view_mode': 'form',
                'name': _('Choose a project'),
                'context': self._context | {'action_arg': action_arg, 'context_keys': context_keys},
                'target': 'new'
            }
        return action
    
    
    def _automate_context_and_domain(self, project_id, context_keys, action_arg):
        """ When project is known, add relevant keys (project's & possibly others)
            in `context` and part in `domain`

            note: both action_dict['context'] and action_dict['domain'] can be str or python object
            depending `action_arg` was a dict or a XML_ID
        """
        action_dict = self._resolve_action_arg(project_id, action_arg)
        res_model = action_dict.get('res_model')

        # Update context to add project's default keys
        context = _resolve_string_to_python(action_dict.get('context'))
        action_dict['context'] = (
            {k: v for k, v in self._context.items() if k not in ['action_arg', 'context_keys']}
            | context
            | {key: project_id.id for key in context_keys}
        )
        
        # Filter on the project
        if res_model == 'project.project':
            action_dict['res_id'] = project_id.id
        else:
            domain = _resolve_string_to_python(action_dict.get('domain'))
            domain = safe_eval(domain) if isinstance(domain, str) else domain or []
            action_dict['domain'] = expression.AND([
                domain,
                [('project_id', '=', project_id.id)]
            ])

        # Prefix action's name with project's
        project_id = project_id.with_context(action_dict['context'])
        action_dict['display_name'] = '{} / {}' . format(
            project_id.display_name,
            action_dict.get('display_name', action_dict['name'])
        )

        return action_dict


    def _resolve_action_arg(self, project_id, action_arg):
        # 1. a python dict of action
        if isinstance(action_arg, dict):
            return action_arg
        
        elif isinstance(action_arg, str):
            return (
                # 2. `action_arg` is a method of project.project
                getattr(project_id, action_arg)() if hasattr(project_id, action_arg)

                # 3. XMLID
                else self.env['ir.actions.act_window']._for_xml_id(action_arg)
            )
        
        else:
            raise exceptions.ValidationError(_(
                'Unexpected action after choosing the project (%s).',
                action_arg
            ))
