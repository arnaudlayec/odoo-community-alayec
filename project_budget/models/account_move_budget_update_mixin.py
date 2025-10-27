# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMoveBudgetUpdateMixin(models.AbstractModel):
    _name = "account.move.budget.update.mixin"
    _description = "Account Move Budget Update Mixin"

    #===== CRUD =====#
    # For `project_budget_timesheet`
    # However, it could be used to avoid heavy consumming @depends in other models
    @api.model
    def _update_budget_crud(self, method, fields):
        """ To configure in inheriting model
            Called from every `crud` methods (create, copy, write, unlink)

            :arg method: CRUD method ('create', 'write' or 'unlink')
            :option fields: list modified fields (for 'write')
        """
        return self
    
    def _should_update(self, method, fields, fields_depend):
        """ Tool method used in `_update_budget_crud` """
        return (
            method != 'write' # 'create', 'copy', 'unlink'
            or any([x in fields for x in fields_depend]) # for `write`
        )
    
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)._update_budget_crud('create', fields=[])

    def copy(self, default={}):
        res = super().copy(default)
        res._update_budget_crud('copy', fields=[])
        return res

    def write(self, vals):
        res = super().write(vals)
        self._update_budget_crud('write', fields=vals.keys())
        return res
    
    def unlink(self):
        self._update_budget_crud('unlink', fields=[])
        return super().unlink()
