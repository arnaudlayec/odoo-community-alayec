# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

from collections import defaultdict

class Task(models.Model):
    _inherit = ['project.task']

    #===== Fields methods =====#
    @api.model
    def default_get(self, default_fields):
        vals = super().default_get(default_fields)
        print('==== default_get (project_task_analytic_hr) ====')

        if all(x in default_fields for x in ['analytic_account_id', 'type_id']):
            vals = self._set_default_analytic_per_type(vals)
        
        return vals
    
    #===== Compute =====#
    @api.depends('type_id', 'type_id.analytic_account_id')
    def _compute_analytic_account_id(self):
        """ Overwrite base compute method
            If type is explicitely changed by user:
            - overwrite any posisble HR analytic information written on task from
              module `project_task_analytic_hr`
            - leave default analytic account (project's) in place if the new type does not have
              any analytic account configured
        """
        super()._compute_analytic_account_id()
        
        # don't override default from ctx (e.g. Kanban column)
        if self._context.get('default_analytic_account_id'):
            return
        
        for task in self:
            if task.is_analytic_account_id_changed or task.type_id.id:
                task.analytic_account_id = task.type_id.analytic_account_id
    
    #===== Business Logics for analytic account per task' type =====#
    def _set_default_analytic_per_type(self, vals={}):
        """ If a default Analytic Account is set on Type, overwrite **only(1)** default
            Task analytic (which normally follows project's analytic) to its
            type's analytic

            (1) allowing priority to module `project_task_analytic_hr` to set task analytic
             based on HR information, and not type information
        """
        project_id = vals.get('project_id', self.env.context.get('default_project_id'))

        if project_id:
            project = self.env['project.project'].browse(project_id)
            analytic_id = vals.get('analytic_account_id') or self._context.get('default_analytic_account_id')
            is_default = not analytic_id or project.analytic_account_id.id == analytic_id

            if is_default:
                type_id = self._get_default_type_id(vals)
                
                if type_id:
                    type = self.env['project.type'].browse(type_id)
                    vals['analytic_account_id'] = type.analytic_account_id.id or analytic_id
        
        return vals

    def _get_default_type_id(self, vals):
        return vals.get('type_id', self.env.context.get('default_type_id'))
