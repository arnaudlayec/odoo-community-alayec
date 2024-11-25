# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Task(models.Model):
    _inherit = ["project.task"]

    #===== Fields' method =====#
    def _get_default_stage_id(self):
        """ Gives default stage_id: override so stages are shared between projects """
        return self.env['project.task.type'].search([], limit=1).id
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Do not show personal stage on `My Task` Kanban """
        return self.env['project.task.type'].search([('user_id', '=', False)])
    
    #===== Fields =====#
    stage_id = fields.Many2one(
        # we don't fully disabled *Personal Stages*, so we filter only on non-user Stages
        domain=[('user_id', '=', False)]
    )

    #===== CRUD =====#
    # def write(self, vals):
    #     """ Allow setting `stage_id` on a task without project """


    #===== Logics =====#
    def _populate_missing_personal_stages(self):
        """ If wanted to fully disable *Personal Stage*,
            return an empty result without calling *super()* 
        """
        res = super()._populate_missing_personal_stages()
        self.env['project.task.type'].sudo().search([('user_id', '!=', False)]).active = False
        return res
