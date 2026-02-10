# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ImportApiLine(models.Model):
    _name = 'import.api.line'
    _description = 'API log line'
    _rec_name = 'display_name'
    _order = "create_date DESC, external_ref ASC, id ASC"

    #===== Fields' methods =====#
    def _selection_record_ref(self):
        Model = self.env['ir.model'].sudo()
        return [
            (x['model'], x['name']) for x
            in Model.search_read([], ['model', 'name'])
        ]

    #===== Fields =====#
    # api logger
    logger_id = fields.Many2one(
        comodel_name='import.api.call',
        string='API call',
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(related="logger_id.company_id",)
    active = fields.Boolean(related='logger_id.active',store=True,)
    model = fields.Char(string='Model',readonly=True,)
    model_description = fields.Char(
        compute="_compute_model_description",
    )
    # line
    state = fields.Selection(
        selection=[
            ('global', "Global line"),
            ('success', "Success"),
            ('info', "Information"),
            ('warning', "Imported with defect"),
            ('error', "Not imported"),
        ],
        compute='_compute_state',
        default='error',
        store=True,
    )
    verified = fields.Boolean(
        string='Verified',
        compute='_compute_verified',
        default=False,
        store=True,
        readonly=False,
    )
    external_ref = fields.Char(string='External Ref.', readonly=True,)
    message = fields.Text(string='Message', readonly=True,)
    field = fields.Char(string='Field', help='In payload', readonly=True,)
    value = fields.Char(string='Value', readonly=True,)
    record_id = fields.Many2oneReference(string='Odoo ID', readonly=True,)
    record_ref = fields.Reference(
        string="Record",
        compute='_compute_record_ref',
        selection='_selection_record_ref',
    )

    #===== Compute =====#
    def _compute_display_name(self):
        for line in self:
            line.display_name = "%(external_ref)s%(separator)s%(record_ref)s" % {
                "external_ref": line.external_ref or '',
                "separator": ' -> ' if line.external_ref and line.record_ref else '',
                "record_ref": line.record_ref or '',
            }
    
    @api.depends("model")
    def _compute_model_description(self):
        for line in self:
            if not line.model in self.env:
                line.model_description = _("Unknown model")
            else:
                line.model_description = _(line.env[line.model]._description)
    
    @api.depends('record_id', 'model')
    def _compute_record_ref(self):
        """ Find which of fields in `_get_record_fields`
            is defined, for display in list view
        """
        for line in self:
            line.record_ref = (
                f"{line.model},{line.record_id}"
                if line.model in self.env and line.record_id
                else False
            )

    @api.depends('record_id', 'message')
    def _compute_state(self):
        manual_states = ["warning", "success"]
        for line in self:
            # computed
            if not line.external_ref:
                line.state == 'global'
            elif not line.record_id:
                line.state = 'error'
            # 'warning' and 'success' can be manually written
            elif line.state not in manual_states:
                if line.message:
                    line.state = 'info'
                else:
                    line.state = 'success'
    
    @api.depends("state")
    def _compute_verified(self):
        for line in self:
            line.verified = bool(line.state == "success")
    
    #===== Logics =====#
    def _display(self):
        """ :arg line: either a log.line `record` or `vals` dict """
        report = _(
            "%s | External ID: %s | Model: %s | Odoo ID: %d",
            self.message, self.external_ref, self.model, self.record_id,
        )
        if self.field:
            report += _(" | Field: %s", self.field)
        if self.value:
            report += _(" | Value: %s", self.value)
        return report

    #===== Actions =====#
    def action_open_record_ref(self):
        """ When clicking import.api.line record from List view,
            open either the record, either line details
        """
        self.ensure_one()
        if not self.record_ref:
            return {
                'type': 'ir.actions.act_window',
                'res_model': "import.api.line",
                'view_mode': 'form',
                'name': _("API call line"),
                'res_id': self.id,
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.model,
                'view_mode': 'form',
                'name': self.record_ref.display_name,
                'res_id': self.record_id,
            }
    
    def action_toggle_verified(self):
        verified = self.filtered("verified")
        verified.verified = False
        (self - verified).verified = True
